import json
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .local import local_context
from .models import AudioTrack, DiaryEntry, Journey
from .serializers import DiarySerializer, JourneySerializer


def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"app": "last-train-local", "instance": os.environ.get("LASTTRAIN_INSTANCE", "development")})


@api_view(["GET"])
def csrf(request):
    return Response({"csrf_token": get_token(request)})


@api_view(["GET", "POST"])
def profiles(request):
    context = local_context()
    if request.method == "POST":
        from rest_framework.serializers import IntegerField
        profile_id = IntegerField(min_value=1).run_validation(request.data.get("id"))
        context.owner = get_object_or_404(get_user_model(), pk=profile_id)
        context.save(update_fields=["owner"])
    return Response({"selected": context.owner_id, "profiles": [
        {"id": user.pk, "name": user.first_name or user.username,
         "journeys": user.journeys.count(), "diary": user.diary_entries.count()}
        for user in get_user_model().objects.order_by("id")]})


@api_view(["GET"])
def data_info(request):
    return Response({"directory": str(settings.DATA_DIR), "backups": sorted(p.name for p in (settings.DATA_DIR / "backups").glob("*.zip"))})


@api_view(["POST"])
def backup(request):
    from local_data import create_backup
    path = create_backup(settings.DATA_DIR)
    return Response({"filename": path.name, "directory": str(path.parent)})


@api_view(["GET"])
def export_data(request):
    data = {"format": "last-train-export-v1", "journeys": JourneySerializer(Journey.objects.filter(user=request.user), many=True).data,
            "diary": DiarySerializer(DiaryEntry.objects.filter(user=request.user), many=True).data}
    response = HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="last-train-export.json"'
    return response


def audio_kind(header):
    if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
        return "wav", "audio/wav"
    if header[:4] == b"OggS":
        return "ogg", "audio/ogg"
    if header[:4] == b"fLaC":
        return "flac", "audio/flac"
    if header[:3] == b"ID3" or (len(header) > 1 and header[0] == 255 and header[1] & 224 == 224):
        return "mp3", "audio/mpeg"
    raise ValidationError({"file": "Use a valid WAV, MP3, Ogg or FLAC audio file (up to 100 MB)."})


@api_view(["GET", "POST"])
def audio_library(request):
    if request.method == "POST":
        upload = request.FILES.get("file")
        if not upload or not 12 <= upload.size <= 100 * 1024 * 1024:
            raise ValidationError({"file": "Select audio up to 100 MB."})
        extension, mime = audio_kind(upload.read(16))
        upload.seek(0)
        filename = f"{uuid.uuid4().hex}.{extension}"
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        target = settings.MEDIA_ROOT / filename
        try:
            with target.open("xb") as stream:
                for chunk in upload.chunks():
                    stream.write(chunk)
            AudioTrack.objects.create(title=Path(upload.name).stem[:200], filename=filename, content_type=mime)
        except Exception:
            target.unlink(missing_ok=True)
            raise
    return Response([{"id": track.pk, "title": track.title, "artist": "Your local library",
                      "url": f"/api/audio/{track.pk}/", "duration": 0} for track in AudioTrack.objects.order_by("id")])


@api_view(["GET"])
def audio_file(request, pk):
    track = get_object_or_404(AudioTrack, pk=pk)
    target = (settings.MEDIA_ROOT / track.filename).resolve()
    if target.parent != settings.MEDIA_ROOT.resolve() or not target.is_file():
        raise Http404
    # Byte ranges support seeking without downloading the entire library track.
    size = target.stat().st_size
    requested = request.headers.get("Range")
    if requested:
        import re
        match = re.fullmatch(r"bytes=(\d+)-(\d*)", requested)
        if not match:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{size}"})
        start = int(match[1])
        end = min(int(match[2]) if match[2] else size - 1, size - 1)
        if start > end:
            return HttpResponse(status=416, headers={"Content-Range": f"bytes */{size}"})
        from django.http import StreamingHttpResponse
        def chunks():
            with target.open("rb") as stream:
                stream.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = stream.read(min(65536, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        return StreamingHttpResponse(chunks(), status=206, content_type=track.content_type,
                                     headers={"Content-Range": f"bytes {start}-{end}/{size}", "Content-Length": end-start+1, "Accept-Ranges": "bytes"})
    return FileResponse(target.open("rb"), content_type=track.content_type, headers={"Accept-Ranges": "bytes"})


def frontend(request, path=""):
    root = settings.FRONTEND_DIR.resolve()
    candidate = (root / path).resolve()
    if not candidate.is_relative_to(root):
        raise Http404
    if path.startswith(("assets/", "art/")) or path in {"favicon-16.png", "favicon-32.png"}:
        if not candidate.is_file():
            raise Http404
        return FileResponse(candidate.open("rb"))
    if path not in ("", "dashboard", "journeys/new", "diary", "atlas", "statistics", "history", "settings", "login", "register"):
        raise Http404
    if not (root / "index.html").is_file():
        return HttpResponse("Build the frontend with the install command for this edition.", status=503)
    return FileResponse((root / "index.html").open("rb"), content_type="text/html")

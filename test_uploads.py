import os
import io
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_media_upload():
    print("Testing multipart file uploads (image + video)...")
    
    # Create fake image bytes (a simple 1x1 PNG or dummy bytes)
    img_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    dummy_video = b"FAKE_VIDEO_CONTENT_FOR_TESTING_PURPOSES"

    files = {
        "cover_image": ("sample_cover.png", io.BytesIO(img_bytes), "image/png"),
        "video": ("sample_clip.mp4", io.BytesIO(dummy_video), "video/mp4")
    }

    data = {
        "experiment_no": "5",
        "title": "Deep Learning with PyTorch",
        "short_description": "Building and training a Convolutional Neural Network for image classification.",
        "d2_heading": "Model Architecture & Accuracy Curves",
        "long_content": "AIM:\nTo construct a CNN model.\n\nPROCEDURE:\n1. Prepare dataset.\n2. Train for 20 epochs.\n\nCONCLUSION:\nAchieved 96.2% test accuracy.",
        "github_url": "https://github.com/alexmorgan-ds/pytorch-cnn"
    }

    r = requests.post(f"{BASE_URL}/api/experiments", data=data, files=files)
    assert r.status_code == 201, f"Upload failed: {r.text}"
    exp = r.json()["data"]
    exp_id = exp["id"]

    cover_url = exp["cover_image"]
    video_url = exp["video"]
    print(f"Uploaded cover URL: {cover_url}")
    print(f"Uploaded video URL: {video_url}")

    assert cover_url and cover_url.startswith("/static/uploads/images/"), "Cover URL missing or incorrect path"
    assert video_url and video_url.startswith("/static/uploads/videos/"), "Video URL missing or incorrect path"

    # Verify files physically exist on disk
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cover_disk_path = os.path.join(base_dir, cover_url.lstrip("/").replace("/", os.sep))
    video_disk_path = os.path.join(base_dir, video_url.lstrip("/").replace("/", os.sep))

    assert os.path.exists(cover_disk_path), f"File {cover_disk_path} does not exist"
    assert os.path.exists(video_disk_path), f"File {video_disk_path} does not exist"
    print("Both image and video files confirmed present on local disk.")

    # Now test single experiment fetch
    r = requests.get(f"{BASE_URL}/api/experiments/{exp_id}")
    assert r.status_code == 200
    single = r.json()["data"]
    assert single["title"] == "Deep Learning with PyTorch"
    print("Single experiment GET with media confirmed.")

    # Now delete experiment and check file cleanup
    r = requests.delete(f"{BASE_URL}/api/experiments/{exp_id}")
    assert r.status_code == 200
    assert not os.path.exists(cover_disk_path), "Cover file should be deleted from disk"
    assert not os.path.exists(video_disk_path), "Video file should be deleted from disk"
    print("Files successfully removed from disk upon experiment deletion.")

    print("\nALL MEDIA UPLOAD AND CLEANUP TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_media_upload()

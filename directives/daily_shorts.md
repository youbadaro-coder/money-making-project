# Daily Shorts Generation Directive

## Goal
Create and upload a high-quality 60-second vertical video (Shorts) to YouTube daily at 9 PM.
Topics should be chosen from: Touching, Nostalgic, Heartbreaking, Cute, Unique.

## Workflow

### 1. Topic & Script Research
- **Tool**: `execution/research_topic.py`
- **Input**: None (Auto-selects topic)
- **Output**: `.tmp/topic_data.json` containing:
  - `topic`: Selected keyword
  - `sub_topic`: Specific subject
  - `script`: 60-second narration/text script
  - `keywords`: For searching stock footage

### 2. Asset Collection
- **Tool**: `execution/fetch_materials.py`
- **Input**: `.tmp/topic_data.json`
- **Output**:
  - `.tmp/videos/`: Directory including 5-7 vertical HD clips
  - `.tmp/music.mp3`: Background music

### 3. Video Editing
- **Tool**: `execution/edit_video.py`
- **Input**: `.tmp/videos/`, `.tmp/music.mp3`, `.tmp/topic_data.json`
- **Output**: `.tmp/final_video.mp4`
- **Requirements**:
  - Resolution: 1080x1920 (9:16)
  - Duration: < 60 seconds
  - Text overlay: Centered, emotional font, readable
  - Music: Fade in/out

### 4. Upload
- **Tool**: `execution/upload_video.py`
- **Input**: `.tmp/final_video.mp4`, `.tmp/topic_data.json`
- **Output**: YouTube Video ID
- **Settings**:
  - Privacy: Public (or Scheduled)
  - Title: From `topic_data.json`
  - Description: Generated description + Hashtags

## Error Handling
- If any step fails, log the error to `execution/logs/error.log`.
- Retry up to 3 times for API failures.

# 🏭 Short Form Factory Upgrade Plan

## 🎯 Objective
Execute the upgrade strategy defined in the meeting log to transform the factory into a "Viral Video Printer".

## 📦 Tasks

### 1. Visual Engine Upgrade (Song Team Leader) <!-- id: 1 -->
- [ ] **Enhance `edit_video.py`**:
    - Improve `create_text_image` for better readability (Stroke, Shadow).
    - Add "Punchy" font settings (larger size, bold).
    - (Optional) Implement basic "Zoom In" effect on images if possible.

### 2. Sourcing Engine Upgrade (Kodari Manager) <!-- id: 2 -->
- [ ] **Enhance `fetch_materials.py`**:
    - Improve search logic: If specific extraction fails, fall back to broader categories.
    - Add logic to download a "High Energy" BGM if none exists.

### 3. Integration & Testing <!-- id: 3 -->
- [ ] **Dry Run**:
    - Execute `research_topic.py` to verify JSON output format.
    - Verify `fetch_materials.py` connects to Pexels (if key exists).
- [ ] **Final Report**:
    - Summarize changes and current capability.

## 📝 Notes
- **Annie's Part**: Already applied (`research_topic.py` prompt update).
- **API Keys**: Requires `PEXELS_API_KEY` and `GEMINI_API_KEY` in `.env`.

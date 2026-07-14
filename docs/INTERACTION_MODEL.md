# Interactive Workstation Interaction Model

The Prompt 21 workstation uses a clinician-controlled interaction model.

## Master Clock

The annotated video is the master clock. During playback, `video.currentTime` is mapped to the nearest processed frame timestamp. The selected frame then drives every synchronized display element.

## Frame Selection

Frames can be selected by:

- video playback time updates,
- previous-frame and next-frame buttons,
- timeline dragging,
- timestamp jump input,
- graph clicks, and
- keyboard shortcuts.

Every selection path calls the same frame-selection routine in the generated viewer. That routine updates the selected processed-frame index and redraws the measurement panel, overlay, graphs, and comparison bars from the same frame record.

## Timeline Dragging

When the user begins dragging the timeline, playback pauses. The workstation seeks instantly to the selected processed frame and updates all analytics from that frame. When dragging ends, playback resumes only if the video was playing when the drag started.

## Keyboard Shortcuts

Keyboard shortcuts are limited to workstation navigation:

- Space toggles play/pause.
- Left arrow pauses and selects the previous processed frame.
- Right arrow pauses and selects the next processed frame.

Inputs and select menus retain normal keyboard behavior.


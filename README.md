# drone-tracker
Tracks a drone flying low against the treeline using method of cross-correlation to find the shift between successive images in video from a hand-held infrared camera. This method works well when the target is flying smoothly against a complex background.  

![Alt text](drone.2.gif?raw=true "Output")

The input video (I'm not free to upload here) was taken with a hand-held longwave infrared camera. The camera operator attempted to keep in the certer of the frames a small drone which was flying low along the treeline in dim light. The drone produces little heat and so the use of the LWIR part of the spectrum was of no aid in this task. Frame registration was performed using cross-correlation (phase correlation). This registration calculated, I could correct for most of the camera motion, however there is some additional motion between frames, that of branches swaying due to wind. This I partially corrected with a morphological open, but larger clusters, corresponding to large sections of branches moving in the wind, I intend to "filter" using a mean-shift tracker (not yet implemented). When you view the output video ("output_colorized.mp4"), you will notice some wild jarring of the camera by the operator; these extremely large camera movements between frames cannot be corrected.

This is not yet a full "tracker", but it locates (colored red) regions in which a target is likely. When the algorithm is included to associate the labeled regions in one frame to those of subsequent frames, and spurious detections are disregarded, then we can call it a tracker.

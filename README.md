When the media moved to the external sd card, but the indices restart anew.

Example: Internal storage:
```
/DCIM/XXX
├── DSC_0001.jpg
├── DSC_0003.jpg
├── MOV_0001.mp4
└── MOV_0002.mp4
```

External SD card:
```
/DCIM/XXX
├── DSC_0001.jpg
├── DSC_0002.jpg
├── DSC_0003.jpg
└── MOV_0001.mp4
```

You run out of storage on the internal storage. Let's move media to the SD card. What could possibly go wrong?

Internal storage:
```
/DCIM/XXX
```

External SD card:
```
/DCIM/XXX
├── DSC_0001.jpg
├── DSC_0001_1.jpg
├── DSC_0002.jpg
├── DSC_0003.jpg
├── DSC_0003_1.jpg
├── MOV_0001_1.mp4
└── MOV_0002.mp4
```

~~Perfect. Who even needs chronological indexing?~~
Repeat ad absurdum. Then try to fix this mess. This is where this tool comes into play.

# Example: Custom EDM track with specific style

music-gen generate \
  --text "Feel the beat, move your feet, electric energy, can't be beat" \
  --genre electronic \
  --duration 240 \
  --verses 2 \
  --choruses 4 \
  --bridge \
  --style "style:progressive house" \
  --style "sound:layered synthesizers with pulsing bass" \
  --style "similar_to:deadmau5" \
  --temperature 0.9 \
  --output custom_edm.mp3

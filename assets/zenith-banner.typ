#set page(width: auto, height: auto, margin: (x: 14pt, y: 10pt), fill: none)

#grid(
  columns: (auto, auto),
  gutter: 22pt,
  align: horizon,
  image("zenith-star.svg", height: 76pt),
  [
    #set text(
      font: ("Inter", "SF Pro Display", "Roboto", "Liberation Sans", "Noto Sans", "Arial", "sans-serif"),
      fill: rgb("#38bdf8"),
      weight: "bold",
    )
    #text(size: 56pt, tracking: 2.5pt)[Zenith]
  ],
)

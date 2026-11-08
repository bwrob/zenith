#set page(width: auto, height: auto, margin: 4pt, fill: none)

#grid(
  columns: (auto, auto),
  gutter: 20pt,
  align: horizon,
  image("zenith-star.svg", height: 64pt),
  [
    #set text(font: ("Inter", "SF Pro Display", "Liberation Sans", "Noto Sans", "sans-serif"))
    #text(
      size: 44pt,
      weight: "bold",
      tracking: 4pt,
      fill: gradient.linear(rgb("#ffffff"), rgb("#e0f2fe"), rgb("#38bdf8")),
    )[ZENITH]
  ],
)

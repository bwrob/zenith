#set page(width: auto, height: auto, margin: (x: 14pt, y: 8pt), fill: none)
#set text(
  font: ("Inter", "SF Pro Display", "Roboto", "Liberation Sans", "Noto Sans", "Arial", "sans-serif"),
  size: 36pt,
  weight: "bold",
  tracking: 1.5pt,
)

#grid(
  columns: (auto, auto),
  gutter: 14pt,
  align: horizon,
  image("python-emblem.svg", height: 38pt),
  box[
    #text(fill: rgb("#387eb8"))[py]#text(fill: rgb("#ffc331"))[thon]
  ],
)

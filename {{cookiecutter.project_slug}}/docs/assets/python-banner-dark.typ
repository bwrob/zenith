#set page(width: auto, height: auto, margin: 4pt, fill: none)

#grid(
  columns: (auto, auto),
  gutter: 18pt,
  align: horizon,
  image("python-emblem.svg", height: 56pt),
  [
    #set text(font: ("Inter", "SF Pro Display", "Liberation Sans", "Noto Sans", "sans-serif"))
    #text(size: 38pt, weight: "bold", tracking: 2pt)[
      #text(fill: gradient.linear(rgb("#58a6ff"), rgb("#387eb8")))[py]#text(fill: gradient.linear(rgb("#ffe873"), rgb("#ffc331")))[thon]
    ]
  ],
)

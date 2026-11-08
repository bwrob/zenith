#set page(width: auto, height: auto, margin: 4pt, fill: none)

#block(
  stroke: 1.25pt + rgb("#000000"),
  radius: 10pt,
  inset: (x: 14pt, y: 8pt),
)[
  #grid(
    columns: (auto, auto),
    gutter: 14pt,
    align: horizon,
    image("python-emblem.svg", height: 48pt),
    [
      #set text(font: "Space Grotesk", size: 68.6pt, weight: "bold", tracking: 2pt)
      #text(stroke: 0.5pt + rgb("#000000"))[
        #text(fill: gradient.linear(rgb("#58a6ff"), rgb("#387eb8")))[py]#text(fill: gradient.linear(rgb("#ffe873"), rgb("#ffc331")))[thon]
      ]
    ],
  )
]

#set page(width: auto, height: auto, margin: 8pt, fill: none)

#block(
  fill: rgb("#060a12"),
  stroke: (
    paint: gradient.linear(
      rgb("#387eb8").transparentize(20%),
      rgb("#ffc331").transparentize(50%),
      rgb("#1e293b"),
      angle: 135deg,
    ),
    thickness: 1.25pt,
  ),
  radius: 16pt,
  inset: (x: 22pt, y: 16pt),
)[
  #grid(
    columns: (auto, auto, auto),
    gutter: 20pt,
    align: horizon,
    image("python-emblem.svg", height: 56pt),
    line(start: (0pt, -26pt), end: (0pt, 26pt), stroke: 1pt + rgb("#1e293b")),
    [
      #set text(font: ("Inter", "SF Pro Display", "Liberation Sans", "Noto Sans", "sans-serif"))
      #stack(
        spacing: 6pt,
        text(size: 36pt, weight: "bold", tracking: 2pt)[
          #text(fill: gradient.linear(rgb("#58a6ff"), rgb("#387eb8")))[py]#text(fill: gradient.linear(rgb("#ffe873"), rgb("#ffc331")))[thon]
        ],
        grid(
          columns: (auto, auto),
          gutter: 8pt,
          align: horizon,
          box(
            fill: rgb("#0c1527"),
            stroke: 0.75pt + rgb("#387eb8").transparentize(40%),
            radius: 4pt,
            inset: (x: 6pt, y: 2.5pt),
            text(size: 8.5pt, weight: "bold", tracking: 1.2pt, fill: rgb("#58a6ff"))[PRODUCTION],
          ),
          text(size: 10pt, weight: "medium", tracking: 1.2pt, fill: rgb("#94a3b8"))[HIGH-VELOCITY STACK],
        ),
      )
    ],
  )
]

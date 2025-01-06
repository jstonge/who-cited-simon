---
toc: false
sql: 
  simon_raw: ./data/a5108357701.parquet
  simon: ./data/a5108357701_topic_net.parquet
  timeseries: ./data/a5108357701_timeseries.parquet
---

# Simon says
## Lets do some Herbert Simonology. 

```sql id=[...simon_raw]
SELECT * FROM simon_raw ORDER BY publication_year
```

According to the [OpenAlex](https://openalex.org/) database, Herbert Simon published a total of ${simon_raw.length} articles in his career.

```js
Plot.plot({
  marginLeft: 50,
  y: {label: "count article", grid: true},
  marks: [
    Plot.rectY(simon_raw, Plot.binX({y: "count"}, {x: "publication_year", ry2: 4, ry1: -4, clip: "frame"})),
    Plot.ruleY([0])
  ]
})
```

Same, but for his most cited work (if you like that kind of stuff): 

```js
Plot.plot({
  marginLeft: 50,
  y: {label: "count article", grid: true},
  marks: [
    Plot.rectY(simon_raw, Plot.binX({y: "sum"}, {x: "publication_year", y: "cited_by_count", ry2: 4, ry1: -4, clip: "frame"})),
    Plot.ruleY([0])
  ]
})
```

The book in 1955 that got Simon to 35K citations is `A Behavioral Model of Rational Choice`, a classic in many fields. But also `ON A CLASS OF SKEW DISTRIBUTION FUNCTIONS`, which is a well know paper in complex systems that discuss heavy-tail distributions appearing in many different natural systems. Here's the full table of his work:

<div class="card", style="padding:0">${
  Inputs.table(simon_raw)
}
</div>

He is known to have publish in a wide variety of field of studies. Here we show the count of papers with associated [primary topics](https://docs.openalex.org/api-entities/topics):

```sql id=topic_count
SELECT COUNT(primary_topic) as n, SUM(cited_by_count) as tot_cit, primary_topic as topic
FROM simon_raw 
WHERE primary_topic NOT NULL
GROUP BY primary_topic
```

```js
const tot_cit = view(Inputs.toggle({label: "Sum citations"}));
```

<div>${resize((width) => Plot.plot({
  width,
  marginBottom: 130,
  x: {tickRotate:20, label: null},
  y: {label: tot_cit ? "sum citations" : "count article", grid: true},
  style: "overflow: visible;",
  marks: [
    Plot.rectY(topic_count, {x: "topic", y: tot_cit ? "tot_cit": "n", ry2: 4, ry1: -4, clip: "frame", sort: {x: '-y', limit: 20}}),
    Plot.ruleY([0])
  ]
}))}</div>

You can select the sum of citations by topics instead of the count of citing articles, if you want. You'll see that the ordering change a little bit, and the distributoin is a bit  more heavytail. It is wild to think that Simon has published over 15 papers on `Sport Psychology and Performance`, while being mostly known for his work on bounded rationality, complex systems, and artificial intelligence.

Now, this is what Simon has done. But I wanted to know who engaged the most with Simon's work. To answer that, we compiled all the papers who cited Simon, by year. With this in hand, we could create the following timeseries:

```sql id=[...ts_citing]
SELECT * from timeseries WHERE type = ${sel_field} ORDER BY publication_year
```

```sql id=[...top_cats]
SELECT SUM(count) as n, category 
from timeseries 
WHERE type = ${sel_field} 
GROUP BY category 
ORDER BY n DESC LIMIT ${top_n}
```

```js
const sel_fieldInput = display(Inputs.select(['domain', 'subfield', 'primary_topic'], {value: 'subfield', label: "Select category"}))
const sel_field = Generators.input(sel_fieldInput)
```

```js
const catego = Array.from(new Set(ts_citing.map(d=>d.category)))
```

```js
const sel_categoInput = display(Inputs.select(catego.sort(), {label: "Select category", multiple: 16, width: 400}))
const sel_catego = Generators.input(sel_categoInput)
```

```js
const top_nInput = display(Inputs.range([0,catego.length > 10 ? 10 : catego.length], {
    label: 'top N', value: catego.length > 10 ? 5 : catego.length, step: 1}))
const top_n = Generators.input(top_nInput)
```

```js
const data_f = sel_catego.length == 0 ? 
    ts_citing.filter(d=>top_cats.map(d => d.category).includes(d.category)) : 
    ts_citing.filter(d=>sel_catego.includes(d.category))
```

<div class="grid grid-cols-3">
    <div class="card grid-colspan-1">
    ${sel_fieldInput}<br>
    ${top_nInput}<br>
    ${sel_categoInput}
    </div>
    <div class="grid-colspan-2">${
        resize((width) => Plot.plot({
    style: "overflow: visible;",
    y: {grid: true, label: "yearly count of papers citing Simon"},
    width,
    color: {legend: true},
    marks: [
        Plot.ruleY([0]),
        Plot.lineY(
            data_f, Plot.windowY({k: 5},
            {x: "publication_year", y: "count", stroke: "category", tip: true})
        )
    ],
    caption: "P.s. But lines are smoothed with k=5"
    })
    )
    }
    </div>
</div>

In the default view, we note the different waves of interest for Simon's work in `Artificial Intelligence`. As expected, `Economics and Econometrics` really like him, most likely for his work on bounded rationality and game theory (confirmed by looking at top `topics` instead of `subfields`, aka `Decision-Making and Behavioral Economics`). I was surprised to see the surge of interests for his work in behavioral economics starting in the 2000s. For some reason, I would've thought that it would've been way earlier. Anyway, the data is there to play with. Here's a small table to find relevant categories using keywords.

#### Table to search categories

```sql id=[...uniq_cat_search]
SELECT category, SUM(count) as n FROM timeseries where type = ${sel_field} GROUP BY category ORDER BY category
```
```js
const selected_cat = view(Inputs.search(uniq_cat_search))
```

<div class="card", style="padding:0">${
  Inputs.table(selected_cat)
}
</div>

In the timeseries, all the subfields are independent of each other. It is informative to look at how clusters of subfields are citing Simon. In the following plot, we look at all **incoming citations** by time periodto Simon's work.

```js
const yr_min = view(Inputs.range([1940, 2024], {step:1, value: 2000}))
const yr_max = view(Inputs.range([1941, 2020], {step:1, value: 2005}))
```

<div class="grid grid-cols-2">
  <div>
    The arc diagram displays subfields co-occurences within papers who cite Simon. Nodes size are in proportion to total citations from a given subfield during that time period to Simon's works (using <code>d3.scaleSqrt().range(3,10)</code>. That is, we map sum of citations to a <a href=https://observablehq.com/@d3/continuous-scales#scale_sqrt>Square root scales</a> bounded between 3 and 10). Additionally, nodes are colored according to their field of research. This is a very neat way to know which subfields citing Simon tend to show up together. 
    <br><br>
    Using knowledge from the previous plot, the default values show subfields citing Simon in the 2000s (say 2000-2005). You can see that now <em>Economics and Econometrics</em> took over the fandom, with <em>Strategy and Management</em> being second. If you go back in the 1960s, you'll see that Simon was originally popular within <em>Artificial intelligence</em> Counting all the subfields, we can see that there there 29 different subfields citing Simon, spanning about 10 different fields (colors)!
    <br><br>
    If you are interested which subfields are citing which papers, here is a small table summarizing that information.
  </div>
  <div>${
    resize((width) => arc(nodes, links, {width}))
  }
  </div>
</div>

```js
const degree = d3.rollup(
  links.flatMap(({ source, target, value }) => [
    { node: source, value },
    { node: target, value }
  ]),
  (v) => d3.sum(v, ({ value }) => value),
  ({ node }) => node
);
```

```js
  const orders = new Map([
    ["by name", d3.sort(nodes.map((d) => d.id))],
    ["by group", d3.sort(nodes, ({group}) => group, ({id}) => id).map(({id}) => id)],
    ["by degree", d3.sort(nodes, ({id}) => degree.get(id), ({id}) => id).map(({id}) => id).reverse()]
  ]);
```

```js
const selected_links = view(Inputs.search(nodesRaw))
```

<div class="card", style="padding:0">${
  Inputs.table(selected_links)
}
</div>

```sql id=[...nodesRaw]
SELECT DISTINCT title, cited_by_count, subfield
FROM simon
WHERE publication_year > ${yr_min} AND publication_year < ${yr_max}
```


```sql id=[...selflinks]
SELECT COUNT(*) as value, source, target 
FROM simon 
WHERE publication_year > ${yr_min} AND publication_year < ${yr_max} AND source = target 
GROUP BY source, target
```

```js
import * as d3 from "npm:d3";
```

```sql id=[...links]
SELECT COUNT(*) as value, source, target 
FROM simon 
WHERE publication_year > ${yr_min} AND publication_year < ${yr_max} AND source != target 
GROUP BY source, target
```


```sql id=[...nodes]
WITH source_target_groups AS (
    SELECT DISTINCT source AS id, source_field AS group
    FROM simon
    WHERE publication_year > ${yr_min} AND publication_year < ${yr_max}

    UNION

    SELECT DISTINCT target AS id, target_field AS group
    FROM simon
    WHERE publication_year > ${yr_min} AND publication_year < ${yr_max}
),
timeseries_summary AS (
    SELECT SUM(count) as n, category as id
    FROM timeseries
    WHERE publication_year > ${yr_min} AND publication_year < ${yr_max} AND type = 'subfield'
    GROUP BY category
)
SELECT 
    sg.id,
    sg.group,
    ts.n,
FROM source_target_groups AS sg
LEFT JOIN timeseries_summary AS ts
ON sg.id = ts.id;

```

```js
function arc(nodes, edges, {width} = {}) {
    const step = 14;
    const marginTop = 20;
    const marginRight = 400;
    const marginBottom = 20;
    const marginLeft = 250;
    const height = (nodes.length - 1) * step + marginTop + marginBottom;
    const y = d3.scalePoint(orders.get("by group"), [marginTop, height - marginBottom]);

    const rScale = d3.scaleSqrt()
        .domain([d3.min(nodes, d => d.n === null ? 0 : d.n), d3.max(nodes, d => d.n)]) // Input range
        .range([5, 15]); 
        
    // A color scale for the nodes and links.
    const color = d3.scaleOrdinal()
    .domain(nodes.map(d => d.group).sort(d3.ascending))
    .range(d3.schemeCategory10)
    .unknown("#aaa");

    // A function of a link, that checks that source and target have the same group andreturns
    // the group; otherwise null. Used to color the links.
    const groups = new Map(nodes.map(d => [d.id, d.group]));
    function samegroup({ source, target }) {
    return groups.get(source) === groups.get(target) ? groups.get(source) : null;
    }

    // Create the SVG container.
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    // The current position, indexed by id. Will be interpolated.
    const Y = new Map(nodes.map(({id}) => [id, y(id)]));

    // Add an arc for each link.
    function arc(d) {
    const y1 = Y.get(d.source);
    const y2 = Y.get(d.target);
    const r = Math.abs(y2 - y1) / 2;
    return `M${marginLeft},${y1}A${r},${r} 0,0,${y1 < y2 ? 1 : 0} ${marginLeft},${y2}`;
    }

    const path = svg.insert("g", "*")
        .attr("fill", "none")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(links)
    .join("path")
        .attr("stroke", d => color(samegroup(d)))
        .attr("d", arc);

    // Add a text label and a dot for each node.
    const label = svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .attr("text-anchor", "end")
    .selectAll("g")
    .data(nodes)
    .join("g")
        .attr("transform", d => `translate(${marginLeft},${Y.get(d.id)})`)
        .call(g => g.append("text")
            .attr("x", -6)
            .attr("font-size", d => rScale(d.n === null ? 0 : d.n))
            .attr("dy", "0.35em")
            .attr("dx", "-0.55em")
            .attr("fill", d => d3.lab(color(d.group)).darker(2))
            .text(d => d.id))
        .call(g => g.append("circle")
            .attr("r", d => rScale(d.n === null ? 0 : d.n))
            .attr("fill", d => color(d.group)));

    // Add invisible rects that update the class of the elements on mouseover.
    label.append("rect")
        .attr("fill", "none")
        .attr("width", marginLeft + 40)
        .attr("height", step)
        .attr("x", -marginLeft)
        .attr("y", -step / 2)
        .attr("fill", "none")
        .attr("pointer-events", "all")
        .on("pointerenter", (event, d) => {
        svg.classed("hover", true);
        label.classed("primary", n => n === d);
        label.classed("secondary", n => links.some(({source, target}) => (
            n.id === source && d.id == target || n.id === target && d.id === source
        )));
        path.classed("primary", l => l.source === d.id || l.target === d.id).filter(".primary").raise();
        })
        .on("pointerout", () => {
        svg.classed("hover", false);
        label.classed("primary", false);
        label.classed("secondary", false);
        path.classed("primary", false).order();
        });
    // Add styles for the hover interaction.
    svg.append("style").text(`
    .hover text { fill: #aaa; }
    .hover g.primary text { font-weight: bold; fill: #333; }
    .hover g.secondary text { fill: #333; }
    .hover path { stroke: #ccc; }
    .hover path.primary { stroke: #333; }
    `);
    // A function that updates the positions of the labels and recomputes the arcs
    // when passed a new order.
    function update(order) {
    y.domain(order);
    label
        .sort((a, b) => d3.ascending(Y.get(a.id), Y.get(b.id)))
        .transition()
        .duration(750)
        .delay((d, i) => i * 20) // Make the movement start from the top.
        .attrTween("transform", d => {
            const i = d3.interpolateNumber(Y.get(d.id), y(d.id));
            return t => {
            const y = i(t);
            Y.set(d.id, y);
            return `translate(${marginLeft},${y})`;
            }
        });
    path.transition()
        .duration(750 + nodes.length * 20) // Cover the maximum delay of the label transition.
        .attrTween("d", d => () => arc(d));
    }

    return svg.node()
}

```



<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

#small-caps {
  font-variant-caps: small-caps;
}  


</style>
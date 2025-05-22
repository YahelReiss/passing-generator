fetch("http://localhost:8000/graph")
  .then(res => res.json())
  .then(data => {
    const svg = d3.select("svg");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    const nodes = data.nodes.map(d => ({ id: d }));
    const links = data.edges.map(([source, target], i) => ({
      source,
      target,
      tag: data.tags[i]
    }));

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.selectAll("line")
      .data(links)
      .enter().append("line");

    const edgeLabels = svg.selectAll("text.edge")
      .data(links)
      .enter().append("text")
      .attr("class", "edge")
      .text(d => d.tag);

    const node = svg.selectAll("circle")
      .data(nodes)
      .enter().append("circle")
      .attr("r", 20);

    const labels = svg.selectAll("text.node")
      .data(nodes)
      .enter().append("text")
      .attr("class", "node")
      .text(d => d.id);

    simulation.on("tick", () => {
      node.attr("cx", d => d.x)
          .attr("cy", d => d.y);

      labels
        .attr("x", d => d.x)
        .attr("y", d => d.y + 5);

      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      edgeLabels
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
    });
  });

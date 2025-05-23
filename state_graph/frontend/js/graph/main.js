function renderGraph(numBalls, maxThrow) {
    fetch(`http://127.0.0.1:8000/graph?num_balls=${numBalls}&max_throw=${maxThrow}`)
      .then(res => res.json())
      .then(graph => {
        const svg = d3.select("#graph-group");
        svg.selectAll("*").remove();  // Clear previous graph

        const width = window.innerWidth;
        const height = window.innerHeight;

        const simulation = d3.forceSimulation(graph.nodes)
          .force("link", d3.forceLink(graph.edges).id(d => d.id).distance(150))
          .force("charge", d3.forceManyBody().strength(-300))
          .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
          .selectAll("path")
          .data(graph.edges)
          .enter()
          .append("path")
          .attr("fill", "none")
          .attr("stroke", "#999")
          .attr("stroke-width", 2)
          .attr("marker-end", d => d.source.id === d.target.id ? null : "url(#arrow)");

        const edgeLabels = svg.append("g")
          .selectAll("text")
          .data(graph.edges)
          .enter()
          .append("text")
          .text(d => d.label)
          .attr("font-size", 12)
          .attr("fill", "#333");

        const node = svg.append("g")
          .selectAll("g")
          .data(graph.nodes)
          .enter()
          .append("g")
          .call(drag(simulation));

        node.append("circle")
          .attr("r", d => 8 + d.id.length * 2)
          .attr("fill", "steelblue");
        
        const groundState = "x".repeat(numBalls) + "-".repeat(maxThrow - numBalls);
        node.filter(d => d.id === groundState) 
          .append("circle")
          .attr("r", d => 9 + d.id.length * 2)
          .attr("fill", "none")
          .attr("stroke", "red")
          .attr("stroke-width", 2);

        node.append("text")
          .text(d => d.id)
          .attr("text-anchor", "middle")
          .attr("dy", "0.35em")
          .attr("fill", "white")
          .style("font-size", "10px");

        function clearHighlights() {
          d3.selectAll("circle").attr("fill", "steelblue");
          d3.selectAll("path").attr("stroke", "#999").attr("stroke-width", 2);
        }

        node.on("click", (event, clickedNode) => {
          event.stopPropagation();

          clearHighlights();

          const incoming = new Set();
          const outgoing = new Set();

          graph.edges.forEach(edge => {
            if (edge.source.id === clickedNode.id) {
              outgoing.add(edge.target.id);
            }
            if (edge.target.id === clickedNode.id) {
              incoming.add(edge.source.id);
            }
          });

          node.selectAll("circle")
            .attr("fill", d => {
              if (d.id === clickedNode.id) return "gold";
              if (incoming.has(d.id)) return "lightcoral";
              if (outgoing.has(d.id)) return "lightgreen";
              return "steelblue";
            });


          link
          .attr("stroke", d => {
            if (d.source.id === clickedNode.id) return "lightgreen";
            if (d.target.id === clickedNode.id) return "lightcoral";
            return "#999";
          })
          .attr("stroke-width", d =>
            d.source.id === clickedNode.id || d.target.id === clickedNode.id ? 3 : 2
          );

          simulation.force("charge", d3.forceManyBody().strength(d =>
            incoming.has(d.id) || outgoing.has(d.id) || d.id === clickedNode.id ? -50 : -600
          ));

          simulation.force("link").distance(d =>
            d.source.id === clickedNode.id || d.target.id === clickedNode.id ? 100 : 150
          );

          simulation.alpha(1).restart();
        });

        d3.select("svg").on("click", () => {
          clearHighlights();
        });

        simulation.on("tick", () => {
          link.attr("d", d => {
            const sourceX = Math.max(20, Math.min(width - 20, d.source.x));
            const sourceY = Math.max(20, Math.min(height - 20, d.source.y));
            const targetX = Math.max(20, Math.min(width - 20, d.target.x));
            const targetY = Math.max(20, Math.min(height - 20, d.target.y));

            if (d.source.id === d.target.id) {
              const r = 10;
              return `M ${sourceX},${sourceY} m 0,-${r} a ${r},${r} 0 1,1 1,0.0001`;
            } else {
              const dx = d.target.x - d.source.x;
              const dy = d.target.y - d.source.y;
              const dr = Math.sqrt(dx * dx + dy * dy);
              return `M${sourceX},${sourceY}A${dr},${dr} 0 0,1 ${targetX},${targetY}`;
            }
          });

          node.attr("transform", d => {
            d.x = Math.max(20, Math.min(width - 20, d.x));
            d.y = Math.max(20, Math.min(height - 20, d.y));
            return `translate(${d.x},${d.y})`;
          });

          edgeLabels
            .attr("x", d =>
              d.source.id === d.target.id
                ? d.source.x
                : (d.source.x + d.target.x) / 2 + (d.target.y - d.source.y) * 0.1
            )
            .attr("y", d =>
              d.source.id === d.target.id
                ? d.source.y - 32
                : (d.source.y + d.target.y) / 2 - (d.target.x - d.source.x) * 0.1
            );
        });
      });
  }

  function drag(simulation) {
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }

  document.getElementById("generateBtn").addEventListener("click", () => {
    const numBalls = document.getElementById("numBalls").value;
    const maxThrow = document.getElementById("maxThrow").value;
    renderGraph(numBalls, maxThrow);
  });

// Initial render
renderGraph(3, 6);
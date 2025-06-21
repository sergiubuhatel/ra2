import { useEffect, useState } from "react";

function useNodeDrag(sigma, onSelect) {
  const [dragging, setDragging] = useState(null);

  useEffect(() => {
    if (!sigma) return;

    const container = sigma.getContainer();
    const graph = sigma.getGraph();

    function onMouseDown(event) {
      const rect = container.getBoundingClientRect();
      const node = sigma.getNodeAt({
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      });

      if (node) {
        setDragging(node);
        graph.setNodeAttribute(node, "highlighted", true);
        onSelect(graph.getNodeAttributes(node));

        sigma.getCamera().disableDragging();
        event.preventDefault();
      }
    }

    function onMouseMove(event) {
      if (!dragging) return;
      const pos = sigma.viewportToGraph(event);
      graph.setNodeAttribute(dragging, "x", pos.x);
      graph.setNodeAttribute(dragging, "y", pos.y);
      sigma.refresh();
      event.preventDefault();
    }

    function onMouseUp(event) {
      if (dragging) {
        graph.removeNodeAttribute(dragging, "highlighted");
        setDragging(null);

        sigma.getCamera().enableDragging();
        event.preventDefault();
      }
    }

    container.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);

    return () => {
      container.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [sigma, dragging, onSelect]);
}

export default useNodeDrag;

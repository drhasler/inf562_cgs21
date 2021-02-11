const ox = 50, oy = 50, ps = 1;
const inte = 1;

let canvas = d3.select('#robots').append('canvas')
	.style('width', '100%')
	.style('height', '100%')
	.attr('width', 200)
	.attr('height', 200)
	// .style('border', '2px dotted black')
	.style('image-rendering', '-moz-crisp-edges')
	.style('image-rendering', 'pixelated');
let ctxt = canvas.node().getContext('2d');

let base = document.createElement('custom');
let custom = d3.select(base);

function draw(positions, color) {
	let width = 200, height = 200;
	ctxt.clearRect(0, 0, width, height);

  positions.forEach(function (d, i) {
    ctxt.fillStyle = `rgb(${color[i]})`;
    ctxt.fillRect(
      ox + positions[i][2] * ps, oy + positions[i][1] * ps,
      ps, ps
    );
  });
}

(async () => {
	let positions = (await d3.json('problem.json')).starts.map(
		(d, i) => [i, d[1], d[0]]);

	let transitions = (await d3.json('solution.json')).steps.map(d => {
		let ret = [];
		for (let [key, dir] of Object.entries(d))
			ret.push([+key, dir]);
		return ret;
	});

	let color = (await d3.json('bernie.json')).cols;

	draw(positions, color);

	for (let transition of transitions) {
		let p = new Promise(r => setTimeout(r, inte));

		for (let [key, direction] of transition) {
			let pos = positions[key];
			switch (direction) {
				case 'N':
					pos[2] -= 1; break;
				case 'S':
					pos[2] += 1; break;
				case 'E':
					pos[1] += 1; break;
				case 'W':
					pos[1] -= 1; break;
			}
			positions[key] = pos;
		}

    await p;
		draw(positions, color);
	}
})();

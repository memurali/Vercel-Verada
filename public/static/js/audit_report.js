google.charts.load("current", {
    packages: ["corechart"]
});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    const chartdata = {{ chartdata_json | safe }};

    const data = new google.visualization.DataTable();
    data.addColumn("string", "Label");
    data.addColumn("number", "Value");

    chartdata.forEach(item => {
        const value = parseFloat(item[1]);
        if (!isNaN(value)) {
            data.addRow([item[0], value]);
        }
    });

    const options = {
        width: 650,
        height: 400,
        title: "Contamination Summary",
        sliceVisibilityThreshold: 0,
        legend: {
            position: "right",
            alignment: "center"
        }
    };

    const chart = new google.visualization.PieChart(document.getElementById("piechart"));
    chart.draw(data, options);
}
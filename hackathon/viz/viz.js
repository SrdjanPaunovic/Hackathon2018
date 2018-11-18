/**
   @author
   Novak Boskov

   @copyright
   Typhoon HIL Inc.

   @license
   MIT
*/

SERVER_ADDRESS = "http://localhost";
SERVER_PORT = 8000;
refreshRate = 0.01;
/**
 * GET solution's results from the server
 */
function getResults() {
    $.ajax({
        url: SERVER_ADDRESS + ":" + SERVER_PORT + "/results",
        type: 'GET',
        success: data => {
            console.log("Data is here.");
            if (refreshRate != Infinity) {
                // visualize results after refreshRate seconds
                setTimeout(() => {

                    vizResults(data);

                    // Show refresh indicator once at 95% of
                    // refreshRate time
                    $('#refreshIndicator').html('<div class=\"loader\"></div>');
                     setTimeout(() => $('#refreshIndicator').html('')
                               , 0.95 * refreshRate * 1000);

                    // recur to next cycle
                    getResults();
                }, refreshRate * 1200);
            }
        },
        error: (_, __, error) => {
            console.log("Typhoon's framework server responded with an error.\n"
                        + error);

            if (refreshRate != Infinity) {
                setTimeout(() => getResults(), refreshRate * 1000);
            }
        }
    });
}

/**
 * Set page refresh rate from refresh rate input if set or stop refreshing.
 * @param {Bool} stop - stop refreshing
 * @param {Bool} set - set refresh rate using refresh rate input field
 */
function setPageRefresh() {
    var action = $('#action').val()
    if (action == "stop") {
        refreshRate = Infinity;
        $('#refreshRate').val(refreshRate);
        $('#refreshIndicator').html('');
    } else if (action == "set") {
        refreshRate = parseInt($('#refreshRate').val());
        getResults();
    }
}

/**
 * Draw barchart that represents solution's results
 * @param data - json that contains all results sent by the server
 */
var overall_output;

function vizResults(data) {
    var scale = 100;

    // Penalties and costs
    var penalty_num = 0;
    var price = data[data.length - 1].overall;
    var cost = data[data.length - 1].overall_energy;

    // data for the graph 1
    var overall_cost = [];
    var energy_cost = [];
    var penalty_cost = [];
    var computation_cost = [];

    // data for the graph 2
    var total_load =[];
    var pv_power = [];
    var bess_power = [];
    var main_grid_power = [];
    var grid_status = [];
    var bess_soc = [];

    for(var i = 0; i < data.length; i++){
        // Calculate penalty data
        var curr = data[i];
        if(curr.penal > 0){
            penalty_num += 1;
        }

        // Set graph data for graph 1
        overall_cost.push(curr.overall)
        energy_cost.push(curr.overall_energy)
        penalty_cost.push(curr.overall_penalty)
        computation_cost.push(curr.overall_performance)

        // Set graph data for graph 2
        total_load.push(curr.real_load);
        pv_power.push(curr.pv_power);
        bess_power.push(curr.bessPower);
        main_grid_power.push(curr.mainGridPower)
        grid_status.push(curr.DataMessage.grid_status);
        bess_soc.push(curr.bessSOC);

    }

    // Update penalty info on the HTML
    $("#totalcost").html(Math.round(price * 100)/100 + ' $');
    $("#energycost").html(Math.round(cost * 100)/100 + ' $');
    $("#computational_cost").html(Math.round(computation_cost[penalty_cost.length -1 ]  * 100)/100 + ' $');
    $("#penaltycost").html(Math.round(penalty_cost[penalty_cost.length -1 ] * 100)/100 + ' $');
    $("#panaltycounter").html(penalty_num);

    // plots for the graph 1
    var cp_overall_cost = {
      //x: x_size,
      y: overall_cost,
      name: 'Overall cost',
      type: 'scatter'
    };

    var cp_energy_cost = {
      //x: x_size,
      y: energy_cost,
      name: 'Energy cost',
      type: 'scatter'
    };

    var cp_penalty_cost = {
      //x: x_size,
      y: penalty_cost,
      name: 'Penalty cost',
      type: 'scatter'
    };

    var cp_computation_cost = {
      //x: x_size,
      y: computation_cost,
      name: 'Computational cost',
      type: 'scatter'
    };


    // plots for the graph 2
    var cp_total_load = {
      //x: x_size,
      y: total_load,
      name: 'Total Load',
      type: 'scatter'
    };

    var cp_pv_power = {
      //x: x_size,
      y: pv_power,
      name: 'PV Power',
      type: 'scatter'
    };

    var cp_bess_power = {
      //x: x_size,
      y: bess_power,
      name: 'BESS Power',
      type: 'scatter'
    };

    var cp_main_grid_power = {
      //x: x_size,
      y: main_grid_power,
      name: 'Main Grid Power',
      type: 'scatter'
    };

    var cp_grid_status = {
      //x: x_size,
      y: grid_status,
      name: 'Grid Status',
      yaxis: 'y2',
      type: 'scatter'
    };

    var cp_bess_soc = {
      //x: x_size,
      y: bess_soc,
      name: 'Bess SOC',
      yaxis: 'y2',
      type: 'scatter'
    };

    var g1_plot_data = [cp_overall_cost, cp_energy_cost, cp_penalty_cost, cp_computation_cost];
    var g2_plot_data = [cp_bess_power, cp_main_grid_power, cp_total_load, cp_pv_power, cp_grid_status, cp_bess_soc];

    var cp_layout_graph1 = {
        legend: {"orientation": "h"},
        height: 300,
        margin: {
            l: 50,
            r: 50,
            b: 30,
            t: 30,
            pad: 3
        },
        xaxis: {
            showgrid: true,
            zeroline: false,
            showline: true,
            tickangle: 5,
        },
        yaxis: {
            tickangle: 10,
            showline: true,
            showgrid: true,
            zeroline: false,
        },
		paper_bgcolor: 'rgba(0,0,0,0)',
		plot_bgcolor: 'rgba(0,0,0,0)'
    };

    var cp_layout_graph2 = {
        legend: {"orientation": "h"},
        height: 300,
        margin: {
            l: 50,
            r: 50,
            b: 30,
            t: 30,
            pad: 3
        },
        xaxis: {
            showgrid: true,
            zeroline: false,
            showline: true,
            tickangle: 5,
        },
        yaxis: {
            tickangle: 10,
            showline: true,
            showgrid: true,
            zeroline: false,
        },
        yaxis2: {
            tickangle: 10,
            showline: true,
            showgrid: true,
            overlaying: 'y',
            side: 'right'
        },
		paper_bgcolor: 'rgba(0,0,0,0)',
		plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('graph_1', g1_plot_data, cp_layout_graph1);
    Plotly.newPlot('graph_2', g2_plot_data, cp_layout_graph2);

}


/**
 * Runs on <body onload>
 */
function vizOnLoad() {
    $('#refreshRateForm').submit(event => {
        event.preventDefault();
        setPageRefresh();
    });

    getResults();

}

function setAction(action){
    $('#action').val(action)
}

/*
function myViewModel() {
        self.levelRead = ko.observable();
        self.levelData = ko.computed(function () {
            return self.levelRead();
        });
        getResults();
        self.levelRead(overall_output);
        alert(overall_output);
}

ko.applyBindings(new myViewModel());
*/

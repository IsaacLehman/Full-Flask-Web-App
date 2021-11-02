// =============================================================================
// XHR WRAPPER
// FOR GET/POST ENDPOINTS THAT RETURN JSON
//  >> onload = function(<json data|data>)
//
//
//  Example GET: 
//      const jsonRequest = new HttpRequest("GET", "/endpoint/", null, (jsonData)=>{console.log(jsonData)}, (error)=>{console.log(error)})
//
//  Example POST: 
//      const jsonRequest = new HttpRequest("POST", "/endpoint/", {key:value}, (jsonData)=>{console.log(jsonData)}, (error)=>{console.log(error)})
//
// BY: Isaac Lehman
// =============================================================================
class HttpRequest {
    constructor(method, url, data, onload, error) {
        this.method = method;
        this.url = url;
        this.data = data;
        this.onload = onload;
        this.error = error;
        this.xhr = new XMLHttpRequest();

        this.init();
    }

    init() {
        //create XMLHttpRequest object
        this.xhr.open(this.method, this.url)

        if (this.method == "POST") {
            // set content-type header to JSON
            this.xhr.setRequestHeader("Content-Type", "application/json");

            // send JSON data to the remote server
            this.xhr.send(JSON.stringify(this.data));
        } else {
            //send the Http request
            this.xhr.send()
        }

        // set error/load functions
        this.xhr.onload = this.onload;

        this.xhr.onerror = this.onerror;
    }


    set setHeader(key_value) {
        // Set a request header
        this.xhr.setRequestHeader(key_value.key, key_value.value);
    }


    get downloadProgress() {
        // Track data download progress
        // >> in Bytes
        this.xhr.onprogress = function (e) {
            return {
                loaded: e.loaded,
                total: e.total
            }
        }
    }


    get uploadProgress() {
        // Track data upload progress
        // >> in Bytes
        this.xhr.upload.onprogress = function (e) {
            return {
                loaded: e.loaded,
                total: e.total
            }
        }
    }
}

(() => {
    var stats__endpoint = '/api/v1/server-stats/';
    var statsResult = null;
    const jsonRequest = new HttpRequest(
        "GET",                                        // METHOD
        stats__endpoint,                              // URL 
        null,                                         // POST DATA
        (jsonData) => {                               // GOOD RESPONSE
            // PARSE THE JSON
            statsResult = JSON.parse(jsonData.target.response);


            // DATE SETUP
            var dateOptions = {
                axisX: {
                    type: Chartist.FixedScaleAxis,
                    divisor: 5,
                    labelInterpolationFnc: function (value) {
                        return moment(value).format('M-D, h:mm a');
                    }
                }
            }

            // CPU DATA
            var cpuStats = statsResult.cpu.usageSamplings
            var cpuData = Array();

            cpuStats.forEach(element => {
                cpuData.push({
                    x: new Date(element.timestamp),
                    y: element.amount
                });
            });

            var cpuChartData = {
                series: [
                    {
                        name: 'CPU Data',
                        data: cpuData
                    }
                ]
            }
            new Chartist.Line('#cpu-usage', cpuChartData, dateOptions);

            // DISK DATA
            var diskStats = statsResult.disk.samplings;
            var diskMax = statsResult.disk.allowed;
            var diskData = Array();
            var diskMaxLine = Array();

            diskStats.forEach(element => {
                diskData.push({
                    x: new Date(element.timestamp),
                    y: element.amount
                });
                diskMaxLine.push({
                    x: new Date(element.timestamp),
                    y: diskMax
                });
            });

            var diskChartData = {
                series: [
                    {
                        name: 'DISK Data',
                        data: diskData
                    },
                    // {
                    //     name: 'DISK Max Data',
                    //     data: diskMaxLine
                    // }
                ]
            };
            new Chartist.Line('#disk-usage', diskChartData, dateOptions);

            // MEMORY DATA
            var memStats = statsResult.memory.usageSamplings;
            var memData = Array();

            memStats.forEach(element => {
                memData.push({
                    x: new Date(element.timestamp),
                    y: element.amount
                });
            });

            var memChartData = {
                series: [
                    {
                        name: 'MEMORY Data',
                        data: memData
                    }
                ]
            };
            new Chartist.Line('#memory-usage', memChartData, dateOptions);

        },
        (error) => {                                  // BAD RESPONSE
            console.log('ERROR: ', error)
        }
    );

})();



// var chart = new Chartist.Line(
//     '.ct-chart', {
//         series: [
//             {
//                 name: 'series-1',
//                 data: [
//                     { x: new Date(143134652600), y: 53 },
//                     { x: new Date(143234652600), y: 40 },
//                     { x: new Date(143340052600), y: 45 },
//                     { x: new Date(143366652600), y: 40 },
//                     { x: new Date(143410652600), y: 20 },
//                     { x: new Date(143508652600), y: 32 },
//                     { x: new Date(143569652600), y: 18 },
//                     { x: new Date(143579652600), y: 11 }
//                 ]
//             },
//             {
//                 name: 'series-2',
//                 data: [
//                     { x: new Date(143134652600), y: 53 },
//                     { x: new Date(143234652600), y: 35 },
//                     { x: new Date(143334652600), y: 30 },
//                     { x: new Date(143384652600), y: 30 },
//                     { x: new Date(143568652600), y: 10 }
//                 ]
//             }
//         ]
//     }, {
//         axisX: {
//             type: Chartist.FixedScaleAxis,
//             divisor: 5,
//             labelInterpolationFnc: function (value) {
//                 return moment(value).format('MMM D');
//             }
//         }
//     }
// );

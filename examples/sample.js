// Example JavaScript code with issues

function calculateSum(arr) {
    let sum = 0;
    for (let i = 0; i < arr.length; i++) {
        sum += arr[i];
    }
    return sum;
}

// Security issue: eval usage
function executeCode(code) {
    eval(code); // Dangerous!
}

// Missing error handling
async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}

// Callback hell
function processData(callback) {
    getData(function(data) {
        processStep1(data, function(result1) {
            processStep2(result1, function(result2) {
                callback(result2);
            });
        });
    });
}

console.log(calculateSum([1, 2, 3, 4, 5]));

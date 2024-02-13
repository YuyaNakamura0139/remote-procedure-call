const net = require('net');
const readline = require("readline");
const config = require('./config.json');

function createReadlineInterface() {
    return readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
}

function readUserInput(question) {
    const rl = createReadlineInterface();
    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            resolve(answer);
            rl.close();
        });
    });
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min);
}

async function connectToServer(client, request) {
    return new Promise((resolve, reject) => {
        client.connect(config['server_address'], () => {
            console.log('Client: connected to server');
            client.write(JSON.stringify(request));
        });

        client.on('data', (data) => {
            console.log('Received:', data.toString());
            client.end();
        });

        client.on('end', () => {
            console.log('Client: disconnected from server');
            resolve();
        });

        client.on('error', (error) => {
            console.error('Connection error:', error);
            reject(error);
        });
    });
}

async function main() {
    const client = new net.Socket();
    const request = {
        "method": "",
        "params": [],
        "param_types": [],
        "id": getRandomInt(1, 10 ** 10)
    };

    try {
        const method = await readUserInput('Please enter a method --> ');
        const paramsInput = await readUserInput('Please enter params separated by spaces. --> ');
        const paramTypesInput = await readUserInput('Please enter params_type separated by spaces. --> ');
        
        request['method'] = method;
        request['params'] = paramsInput.split(" ");
        request['param_types'] = paramTypesInput.split(" ");
        
        console.log(request);
        await connectToServer(client, request);
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

main();
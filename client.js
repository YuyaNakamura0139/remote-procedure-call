const net = require('net');

// https://maku77.github.io/nodejs/io/readline-from-keyboard.html
/**
 * ユーザーからの入力を受け取り、リクエストオブジェクトを構築してコンソールに出力する非同期関数です。
 * ユーザーはメソッド名、パラメータ、パラメータの型を入力します。
 * 入力された情報はリクエストオブジェクトに格納され、乱数生成関数を使用して一意のIDが割り当てられます。
 */

function readUserInput(question) {
    const readline = require("readline").createInterface({
        input: process.stdin,
        output: process.stdout
    });   

    return new Promise((resolve, reject) => {
        readline.question(question, (answer) => {
            resolve(answer);
            readline.close();
        });
    });
}

// https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Math/random
/**
 * 乱数を生成する関数です。
 * @param {number} min - 生成する乱数の最小値（この値を含む）
 * @param {number} max - 生成する乱数の最大値（この値を含まない）
 * @returns {number} min以上max未満の乱数
 */

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min)
}


(async function main() {
    const config = require('./config.json');
    const server_address = config['server_address'];
    const client = new net.Socket();
    const request = {
        "method": "",
        "params": [],
        "params_types": [],
        "id": NaN
    }

    try {
        const method = await readUserInput('Please enter a method --> ');
        const params = await readUserInput('Please enter params separated by spaces. --> ');
        const params_type = await readUserInput('Please enter params_type separated by spaces. --> ');
    
        request['method'] = method;
        request['params'].push(...params.split(" "));
        request['params_types'].push(...params_type.split(" "));
        request['id'] = getRandomInt(1, 10 ** 10)
        console.log(request);

        client.connect(server_address, () => {
            console.log('Client: connected to server')
            client.write(JSON.stringify(request));
        });
        
        client.on('data', (data) => {
            console.log('Received:', data.toString());
            client.end();
        })
        
        client.on('end', () => {
            console.log('Client: disconnected from server')
        })
    } catch (error) {
        console.error('An error occurred:', error);
    }
})();
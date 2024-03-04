// app.js

const socket = io.connect('http://localhost:5000');
console.log("app.js called");
export { socket };
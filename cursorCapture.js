// 艦これCanvas内でのカーソルの座標をログに出力する
// canvasを含むiframeのsrcに書かれているURLにアクセスして、consoleで実行すると使えます

const canvas = document.getElementsByTagName("canvas")[0];
canvas.onmousemove = (e) => console.log(e.offsetX, e.offsetY);

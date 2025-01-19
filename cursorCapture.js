// 艦これCanvas内でのカーソルの座標をログに出力する
// こっちで使える→http://w14h.kancolle-server.com/kcs2/index.php?api_root=/kcsapi&voice_root=/kcs/sound&osapi_root=osapi.dmm.com&version=6.0.1.1&api_token=16d46fabd2ff24c72bddeeac0c877bed6d210118&api_starttime=1737300469815

const canvas = document.getElementsByTagName("canvas")[0];
canvas.onmousemove = (e) => console.log(e.offsetX, e.offsetY);

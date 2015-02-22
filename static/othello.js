
function OthelloModelView() {
    var self = this;
    self.pieceColours = ko.observableArray();
    self.pieceSize = ko.observable(60);
    self.boardSize = ko.observable(4);
    
    self.loadResponse = function(data)
    {
        colours = new Array();
        for (i=0; i<data['size']; i++) {
            colours[i]= new Array();
            for (j=0; j<data['size']; j++) {
                colours[i][j] = "rgb(0,100,00)";
            }
        }
        x = 0;
        for (i=0; i < data['X'].length; i++) {
            x = x+ 1;
            colours[data['X'][i][0]][data['X'][i][1]] = "black";
        }
        for (i=0; i < data['O'].length; i++) {
            x = x + 1;
            colours[data['O'][i][0]][data['O'][i][1]] = "rgb(200,200,200)";
        }
        self.boardSize(data['size']);
        self.pieceColours(colours);
        self.pieceSize(500/data['size'])
    };
    
    $.getJSON('/game/40481/1', self.loadResponse);

    
    self.clickPiece = function(x, y) {
        alert("x=" + x + "; y=" + y);  
    };
}

ko.applyBindings(new OthelloModelView());
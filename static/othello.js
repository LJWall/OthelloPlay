
Array.prototype.has=function(v){
    for (i=0;i<this.length;i++){
        if (this[i]==String(v)) return true;
    }
    return false;
}

function OthelloModelView() {
    var self = this;
    self.pieceColours = ko.observableArray();
    self.pieceSize = ko.observable(500/8);
    self.boardSize = ko.observable(8);
    self.boardLoaded = ko.observable(false);
    self.blackScore = ko.observable();
    self.whiteScore = ko.observable();
    self.blackToPlay = ko.observable();
    self.gameComplete = ko.observable();
    
    colours = new Array();
    for (i=0; i<self.boardSize(); i++) {
        colours[i]= new Array();
        for (j=0; j<self.boardSize(); j++) {
            colours[i][j] = "rgb(0,100,00)";
        }
    }
    self.pieceColours(colours);
    
    self.processResponse = function(data){
        self.loadResponse(data);
        if (data['current_turn']=='O') {
            $.ajax(self.data['URIs']['play'], {
                    data: ko.toJSON({play: 'auto'}),
                    type: "post", contentType: "application/json",
                    success: self.processResponse
                });
        }
    };
    
    self.loadResponse = function(data) {
        self.data = data;
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
        self.pieceSize(500/data['size']);
        self.blackScore(data['X'].length);
        self.whiteScore(data['O'].length);
        self.blackToPlay(data['current_turn']=='X');
        self.gameComplete(data['game_complete']);
        self.boardLoaded(true);
        location.hash = data['URIs']['get'];
    };
    

    
    self.clickPiece = function(x, y) {
        if (self.boardLoaded()) {
            if (self.data['plays'].has([x, y])) {
                $.ajax(self.data['URIs']['play'], {
                    data: ko.toJSON({play: [x, y]}),
                    type: "post", contentType: "application/json",
                    success: self.processResponse
                });
            }
            else {
                alert('Invalid move');
            }
        }
        
    };
    
    
    sammyApp = Sammy(function() {
        this.get(/\#(.*)/, function() {
                if (!self.boardLoaded() || this.params['splat'] != self.data['URIs']['get']) {
                    $.getJSON(this.params['splat'], self.loadResponse);   
                }
            });
        });
    sammyApp.run();
    
    //$.getJSON('/game/65630/0', self.loadResponse);
}

ko.applyBindings(new OthelloModelView());
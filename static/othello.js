
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
    self.gameComplete = ko.observable(false);

    self.defaultMsgText = 'To save a game and return to it latter just bookmark the page.  Should you wish to amend a move (or two) use the broser back button.';
    self.defaultMsgClass = 'alert alert-info';

    self.msgText = ko.observable(self.defaultMsgText);
    self.msgClass = ko.observable(self.defaultMsgClass);
    
    self.boardSizeOptions = [{size: 6, text: '6 x 6'}, {size: 8, text: '8 x 8'}, {size: 10, text: '10 x 10 (for the committed)'}];
    self.newGameSize = ko.observable(self.boardSizeOptions[1]);

    self.makeBoardArray = function(size) {
        colours = new Array();
        for (i=0; i<size; i++) {
            colours[i]= new Array();
            for (j=0; j<size; j++) {
                colours[i][j] = "rgb(0,100,00)";
            }
        }
        return colours;
    };
    self.pieceColours(self.makeBoardArray(self.boardSize()));
    
    self.processResponse = function(data){
        self.loadResponse(data);
        if (data['current_turn']=='O' && !data['game_complete']) {
            $.ajax(self.data['URIs']['play'], {
                    data: ko.toJSON({play: 'auto'}),
                    type: "post", contentType: "application/json",
                    success: self.processResponse
                });
        }
    };
    
    self.loadResponse = function(data) {
        self.data = data;
        colours = self.makeBoardArray(data['size']);
        for (i=0; i < data['X'].length; i++) {
            colours[data['X'][i][0]][data['X'][i][1]] = "black";
        }
        for (i=0; i < data['O'].length; i++) {
            colours[data['O'][i][0]][data['O'][i][1]] = "rgb(200,200,200)";
        }
        self.boardSize(data['size']);
        self.pieceColours(colours);
        self.pieceSize(500/data['size']);
        self.blackScore(data['X'].length);
        self.whiteScore(data['O'].length);
        self.blackToPlay(data['current_turn']=='X');
        self.gameComplete(data['game_complete']);
        if (data['game_complete']) {
            if (data['X'].length > data['O'].length) {
                self.msgText('Congratulations! You won by ' + String(data['X'].length - data['O'].length) + ' points.');
                self.msgClass('alert alert-success');
            } else if (data['X'].length < data['O'].length) {
                self.msgText('Game over. Computer won by ' + String(data['O'].length - data['X'].length) + ' points.');
                self.msgClass('alert alert-danger');
            } else {
                self.msgText('It\' a draw..');
                self.msgClass('alert alert-warning');
            }
        }
        self.boardLoaded(true);
        location.hash = data['URIs']['get'];
    };
    

    
    self.clickPiece = function(x, y) {
        if (self.boardLoaded() && !self.gameComplete()) {
            if (self.data['plays'].has([x, y])) {
                self.msgText(self.defaultMsgText);
                self.msgClass(self.defaultMsgClass);
                $.ajax(self.data['URIs']['play'], {
                    data: ko.toJSON({play: [x, y]}),
                    type: "post", contentType: "application/json",
                    success: self.processResponse
                });
            }
            else {
                self.msgText('Invalid move');
                self.msgClass('alert alert-danger');
            }
        }
        
    };
    
    self.newGame = function() {
        $.ajax('/game', {
                    data: ko.toJSON({game_size: self.newGameSize()['size']}),
                    type: "post", contentType: "application/json",
                    success: self.processResponse
                });
    };
    
    sammyApp = Sammy(function() {
        this.get(/\#(.*)/, function() {
                if (!self.boardLoaded() || this.params['splat'] != self.data['URIs']['get']) {
                    $.getJSON(this.params['splat'], self.loadResponse);   
                }
            });
        });
    sammyApp.run();
    
}

ko.applyBindings(new OthelloModelView());
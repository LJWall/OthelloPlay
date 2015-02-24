
Array.prototype.has=function(v){
    for (i=0;i<this.length;i++){
        if (this[i]==String(v)) return true;
    }
    return false;
}

function OthelloModelView() {
    var self = this;
    self.data = ko.observable({board: [["", "", "", ""],["", "", "", ""],["", "", "", ""],["", "", "", ""]], current_turn: "X", game_complete: false});
    //self.data = ko.observable();
    self.pieceColours = ko.observableArray();
    self.pieceSize = ko.observable(500/4);
    self.boardSize = ko.observable(4);
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
        self.data(data);
        //raise "You're here";
        /*colours = self.makeBoardArray(data['size']);
        for (i=0; i < data['X'].length; i++) {
            colours[data['X'][i][0]][data['X'][i][1]] = "black";
        }
        for (i=0; i < data['O'].length; i++) {
            colours[data['O'][i][0]][data['O'][i][1]] = "rgb(200,200,200)";
        }
        self.boardSize(data['size']);
        self.pieceColours(colours);*/
        
        self.pieceSize(500/data.board.length);
        blackScore=0;
        whiteScore=0;
        for (i=0; i<data.board.length; i++) {
            for (j=0; j<data.board.length; j++) {
                if (data['board'][i][j]=='X') {
                    blackScore += 1;
                }
                if (data['board'][i][j]=='O') {
                    whiteScore += 1;
                }
            }
        }
        self.blackScore(blackScore);
        self.whiteScore(whiteScore);
        //self.blackToPlay(data['current_turn']=='X');
        
        //self.gameComplete(data['game_complete']);
        if (data['game_complete']) {
            if (self.blackScore() > self.whiteScore()) {
                self.msgText('Congratulations! You won by ' + String(self.blackScore() - self.whiteScore()) + ' points.');
                self.msgClass('alert alert-success');
            } else if (self.blackScore() < self.whiteScore()) {
                self.msgText('Game over. Computer won by ' + String(self.whiteScore() - self.blackScore()) + ' points.');
                self.msgClass('alert alert-danger');
            } else {
                self.msgText('It\' a draw..');
                self.msgClass('alert alert-warning');
            }
        }
        self.boardLoaded(true);
        location.hash = data['URIs']['get'];
    };
    
    self.getPieceColour = function(x, y) {
        switch(self.data()['board'][x][y]) {
            case 'X':
                return 'rgb(0,0,0)';
            case 'O':
                return 'rgb(200,200,200)';
            case 'P':
                return 'rgb(0,100,00)';
            default:
                return 'rgb(0,100,00)';
        }
    };
    
    self.clickPiece = function(x, y, p_type) {

        if (self.boardLoaded() && !self.data().game_complete) {
            if (self.data().board[x][y]=='P') {
                self.msgText(self.defaultMsgText);
                self.msgClass(self.defaultMsgClass);
                $.ajax(self.data().URIs.play, {
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
                if (!self.boardLoaded() || this.params['splat'] != self.data().URIs.get) {
                    $.getJSON(this.params['splat'], self.loadResponse);   
                }
            });
        });
    sammyApp.run();
    
}

ko.applyBindings(new OthelloModelView());
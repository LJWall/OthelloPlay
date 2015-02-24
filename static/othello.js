
Array.prototype.has=function(v){
    for (i=0;i<this.length;i++){
        if (this[i]==String(v)) return true;
    }
    return false;
}

function OthelloModelView() {
    var self = this;
    
    // Board state
    self.data = ko.observable({board: [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]],
                              current_turn: "X",
                              game_complete: false});
    self.pieceSize = ko.observable(500/6);
    self.boardSize = ko.observable(6);
    self.boardLoaded = ko.observable(false);
    
    // Score board info
    self.blackScore = ko.observable();
    self.whiteScore = ko.observable();
    self.blackToPlay = ko.observable();
    self.gameComplete = ko.observable(false);

    //Message and warning info
    self.defaultMsgText = 'To save a game and return to it latter just bookmark the page.  Should you wish to amend a move (or two) use the broser back button.';
    self.defaultMsgClass = 'alert alert-info';
    self.msgText = ko.observable(self.defaultMsgText);
    self.msgClass = ko.observable(self.defaultMsgClass);
    
    // New game area
    self.boardSizeOptions = [{size: 6, text: '6 x 6'}, {size: 8, text: '8 x 8'}, {size: 10, text: '10 x 10 (for the committed)'}];
    self.newGameSize = ko.observable(self.boardSizeOptions[1]);
    
    self.processResponse = function(data){
        self.loadResponse(data);
        if (data['current_turn']=='O' && !data['game_complete']) {
            $.ajax(self.data().URIs.play, {
                    data: ko.toJSON({play: 'auto'}),
                    type: "post", contentType: "application/json",
                    success: self.processResponse
                });
        }
    };
    
    self.loadResponse = function(data) {
        self.data(data);
        
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
    
    self.getPieceColour = function(piece_type) {
        switch(piece_type) {
            case 'X':
                return 'rgb(0,0,0)';
                break;
            case 'O':
                return 'rgb(200,200,200)';
                break;
            case 'P':
                return 'rgb(0,100,00)';
                break;
        }
        return 'rgb(0,100,00)';
    };
    
    self.clickPiece = function(x, y) {
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
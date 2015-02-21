
function OthelloModelView() {
    var self = this;
    self.womble = ko.observable("Foo bar spam");
    self.myList = ko.observableArray([1, 2, 3, 4]);
    self.myList2 = ko.observableArray([1, 2, 3, 4]);
    
    self.pieceColours = ko.observableArray([["rgb(0,100,00)","rgb(0,100,00)","rgb(0,100,00)","rgb(0,100,00)"],
                                            ["rgb(0,100,00)","black","rgb(200,200,200)","rgb(0,100,00)"],
                                            ["rgb(0,100,00)","rgb(200,200,200)","black","rgb(0,100,00)"],
                                            ["rgb(0,100,00)","rgb(0,100,00)","rgb(0,100,00)","rgb(0,100,00)"]]);
    
    self.someColour = ko.observable("pink");
    self.someHTML = ko.observable("<b>Foo!</b>");
    
    self.someFunc = function() {
        if (self.someColour()=="black") {
            self.someColour("rgb(200,200,200)");
        }
        else
        {
            self.someColour("black");
        }
    };
    
    self.clickPiece = function() {
        alert('Wombles!');  
    };
}

ko.applyBindings(new OthelloModelView());
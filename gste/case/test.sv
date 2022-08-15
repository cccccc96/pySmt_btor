
module rbFIFO(clock,dataIn,push,pop,dataOut,full,empty);
    parameter	    MSBD = 3;
    parameter	    LAST = 15;
    parameter	    MSBA = 3;
    input	    clock;
    input [MSBD:0]  dataIn;
    input	    push;
    input	    pop;
    output [MSBD:0] dataOut;
    output	    full;
    output	    empty;

    reg [MSBD:0]    mem[0:LAST];
    reg [MSBA:0]    head;
    reg [MSBA:0]    tail;
    reg		    empty;
    reg         full;
    integer	    i;

    initial begin
	for (i = 0; i <= LAST; i = i + 1)
	    mem[i] = 0;
	head = 0;
	tail = 0;
	empty = 1;
    end // initial begin

    always @ (posedge clock) begin
	if (push & ~full) begin
	    mem[head] = dataIn;
	    head = head + 1;
	    empty = 0;
	end // if (push & ~full)
	else if (pop & ~empty) begin
	    tail = tail + 1;
	    if (tail == head)
		empty = 1;
	end // if (pop & ~empty)
    end // always @ (posedge clock)

    assign dataOut = mem[tail];

    assign full = (tail == head) & ~empty;

endmodule // rbFIFO

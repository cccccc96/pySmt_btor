// Ring buffer FIFO.
// head points to the insertion point unless the buffer is full.
// tail points to the first element in the queue unless the buffer is empty.
// A push on a full buffer is a NOOP.
// A pop from an empty buffer is a NOOP.
// If both push and pop are asserted at the same clock cycle, only the push
// operation is performed.
// dataOut gives the first element of the queue unless the buffer is empty,
// in which case its value is arbitrary.

module rbFIFO(clock,rst,dataIn,push,pop,dataOut,full,empty);
    parameter	    MSBD = 3;
    parameter	    LAST = 15;
    parameter	    MSBA = 3;
    input	    clock;
    input	    rst;
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


    always @ (posedge clock) begin
        if (rst) begin
            for (i = 0; i <= LAST; i = i + 1)
                mem[i] = 0;
            head = 0;
            tail = 0;
            empty = 1;
            full = 0;
        end
        else if (push & ~full) begin
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

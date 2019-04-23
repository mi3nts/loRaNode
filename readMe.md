# loRaNode

## Additional Modifications made to the PPD42NS
### PPD42NS
<img src="https://www.shinyei.co.jp/stc/eng/images/pic_PPD42_L.jpg"
     alt="shinyei"
     style="float: left; margin-right: 10px;" />
     <br/>
     
The pins are labeled as '**thresh**', '**P1**', '**+5v**', '**P2**, and '**grnd**'  going from left to write on the figure given above. 

 - Addition of a 10K resisitor between the threshold pin and ground:
 A good read on the mechanism followed is given [here](http://takingspace.org/wp-content/uploads/ShinyeiPPD42NS_Deconstruction_TracyAllen.pdf).

 -  Use of 2 outputs rather than one:
 ShSome sources suggest that pulses at the P1 output correspond to 1µm particles,
and pulses at the P2 output correspond to 2.5µm particles

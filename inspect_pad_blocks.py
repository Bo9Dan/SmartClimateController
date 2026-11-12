import library_io as io,struct
n=io.setup('PcbLib1.PcbLib');x=n['streams'][215];p=4+struct.unpack_from('<I',x)[0];print('start',p,x[p])
blocks=[];p+=1
for j in range(6):
 z=struct.unpack_from('<I',x,p)[0];blocks.append(x[p+4:p+4+z]);p+=4+z
print([len(b) for b in blocks]);print('core',blocks[4].hex()[:140]);print('remaining',x[p:p+10].hex())

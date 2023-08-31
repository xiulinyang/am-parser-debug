import jnius_config
jnius_config.add_options('-Xmx2G')
jnius_config.set_classpath('am-tools.jar')
from jnius import autoclass

if __name__ == "__main__":
    IRTBCodec = autoclass('de.up.ling.irtg.codec.BinaryIrtgInputCodec')
    codec = IRTBCodec()
    FileInputStream = autoclass('java.io.FileInputStream')
    stream = FileInputStream("test.irtb")
    irtg = codec.read(stream)
    print(irtg)
    print(irtg.toString())


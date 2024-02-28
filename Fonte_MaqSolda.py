#ULTIMA VERSAO 01.12.2023
#Software de captura e gravacao de imagens de duas cameras simultaneas
#para utilização na Máquina de Solda - Decapagem 3 (Empresa ********)

#import das bibliotecas
import numpy as np
import logging as log
import OpenOPC, pywintypes, time, cv2

cam_sup = 'http://<user>:<password>@<ip>:<port>/cgi-bin/mjpg/video.cgi?channel=1&subtype=1'          #input da camera IP
path = "C://_dev//ProjetoMaquinaSolda//ControleDeVersao//Nova pasta//record//"

log.basicConfig(level=log.INFO, filename=path+"LOG.log", 
                format="%(asctime)s - %(levelname)s - %(message)s")         #configuracao do formato do log

def record(p_weld_act, p_weld_no, p_coil_ID):                               #funcao de gravacao que recebe os parametros do PLC 
    current_time = time.localtime()                                         #armazena o horario atual em current_time
    time_string = time.strftime("_%d%m%Y_%H%M%S", current_time)              #formata o current time no formato desejado

    #file_name_sup = "superior_" + time_string + ".avi"                     #nomeia o arquivo da camera superior
    #file_name_inf = "inferior_" + time_string + ".avi"                     #nomeia o arquivo da camera inferior

    #padrao correto
    file_name_sup = "WNo_" + str(int(p_weld_no)) + "_ID_" + str(p_coil_ID) + time_string + "_superior.avi"  #nomeia o arquivo da camera superior   
    file_name_inf = "WNo_" + str(int(p_weld_no)) + "_ID_" + str(p_coil_ID) + time_string + "_inferior.avi"  #nomeia o arquivo da camera inferior   
 
    try:
        cap_inf = cv2.VideoCapture(0)                                       #leitura da webcam
        cap_sup = cv2.VideoCapture(cam_sup)                                 #leitura da camera ip
        log.debug("camera aberta com sucesso")
        pass 
    except:
        log.critical("erro ao ler a camera")                                #log de erro ao ler a camera        
   
    out_cam_sup = cv2.VideoWriter(path+file_name_sup,
    cv2.VideoWriter_fourcc(*"XVID"), 30.0,(640,480))                        #cria o arquivo em formato AVI
    out_cam_inf = cv2.VideoWriter(path+file_name_inf,
    cv2.VideoWriter_fourcc(*"XVID"), 30.0,(640,480))                        #cria o arquivo em formato AVI 
    log.debug("arquivo criado com sucesso")
    
    while p_weld_act:
        log.debug("entrou no laço de gravacao com sucesso")
        ret_sup, frame_sup = cap_sup.read()                                 #lê a camera superior 
        ret_inf, frame_inf = cap_inf.read()                                 #lê a camera inferior
        width = int(cap_inf.get(3))                                         #salva a largura na variavel
        height = int(cap_inf.get(4))                                        #salva a altura na variavel
        
        image = np.zeros((480, 640 * 2, 3), np.uint8)                       #redimensiona a imagem a ser exibida (*2 por serem duas)
        smaller_frame = cv2.resize(frame_sup, (640,480), fx=0.5, fy=0.5)    #redimensiona o frame da cam superior      
        smaller_frame1 = cv2.resize(frame_inf, (640,480), fx=0.5, fy=0.5)   #redimensiona o frame da cam inferior
        image[:height,:width] = smaller_frame                                   
        image[:height,width:] = smaller_frame1
           
        try:
            out_cam_sup.write(frame_sup)                                    #grava o video da camera superior
            out_cam_inf.write(frame_inf)                                    #grava o video da camera inferior
            log.debug("gravou no arquivo com sucesso")
            pass
        except:
            log.error("nao foi possivel gravar o arquivo")                  #erro de gravacao do arquivo       
        try:    
            cv2.imshow('Maquina de Solda', image)                           #exibe o video de ambas as imagens lado a lado
            log.debug("abriu a camera com sucesso")
            pass
        except:
            if not cap_sup.isOpened() or not cap_inf.isOpened:              #condicao pra verificar a abertura correta das cameras
                log.critical("erro ao abrir a camera")                      #log critico de abertura de camera
                
        events = opc.read(itens, group='Group0', update=1)                  #continua a leitura do OPC dentro da gravaçao
        weld_no =  events[0][1]                                             #atribui o valor do numero da solda a variavel
        weld_act = events[1][1]                                             #atribui o valor da ativacao da solda a variavel
        coil_ID = events[2][1]                                              #atribui o valor do numero da bobina a variavel
 

        c = cv2.waitKey(1)
        if c == 27 or not weld_act:                                              #permite sair da janela de gravaçao com ESC ou ao ler a variavel teste no OPC sendo Falsa
            break
        

    cap_sup.release()                                                            #fecha a tela do video superior
    cap_inf.release()                                                            #inferior
    out_cam_sup.release()                                                        #finaliza a gravaçao superior
    out_cam_inf.release()                                                        #inferior
    cv2.destroyAllWindows()                                                      #fecha todas janelas


# Create OPC DA client object
pywintypes.datetime = pywintypes.TimeType
opc = OpenOPC.client()                                                          #atribui o cliente a variavel OPC
opc.connect('<V.Kepware>', '<IP>')                                              #cria a conexao com o PLC

itens = ['DEC3_Siemens.PLC_STR.Numero_Solda',
         'DEC3_Siemens.PLC_STR.Solda_Ativa', 
         'DEC3_Siemens.PLC_STR.ID_Entrada']                                     #coloca a especificacao das TAGs a serem lidas

tecla_esc = 1
last_weld_no = 0
log.info("Hora de start do programa.")
while tecla_esc != 0:                                                           #laço para leitura dos dados OPC
    try:
        events = opc.read(itens, group='Group0', update=1)
        weld_no =  events[0][1]
        weld_act = events[1][1]                                                 #atribui o valor booleano a weldAct
        coil_ID = events[2][1]
        log.debug("conectado")
        print('weldNo: '+ str(weld_no) + '   weldAct: ' + str(weld_act) + '   Coil ID: ' + str(coil_ID))
        
        if (last_weld_no != weld_no) and weld_act:
            last_weld_no = weld_no
            record(weld_act, weld_no, coil_ID)
            
    except:
        opc.connect('<V.Kepware>', '<IP>')                                      #reconecta no PLC caso caia a conexao
        log.debug("reconectando")
        pass
  
    cv2.destroyAllWindows()
    time.sleep(1)

#pyinstaller --hiddenimport win32timezone -F --onefile --paths=C:\_dev\OPCVideoRecorder\venv\Lib\site-packages .\Fonte_MaqSolda.py


#TAGS de leitura 
#Numero_Solda; ID_Entrada; Solda_Ativa.
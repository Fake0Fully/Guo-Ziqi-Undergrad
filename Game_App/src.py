from Tkinter import *
import random
import time

"""This is a pattern recognition game, where player will be given a set of shapes. There will be a classification standard each round.
Player can choose whether the shape belongs to the unknown group. Points will be accumulated to proceed to next round.
The generation of shapes and classification standards is realized by a randomizer.
The game aims to practice player's pattern recognition capability and graphic memory.
Moreover, the process of guessing out the hidden group simulates the process of debugging in programming.
It's an easy but extremely interesting game. Enjoy it!"""
#CONSTRUCTER
class game:
    def __init__(self):
        self.window = Tk()#MAIN DISPLAY WINDOW
        self.window.title("FIND THE HIDDEN GROUP")
        self.c = Canvas(self.window,width = 500,height= 500,bg='azure')
        self.c.pack()
        self.c.focus_set()
        self.c.create_text(110,190,text='Pattern Recognition Game',fill='dim gray',anchor = 'nw',font = 'Calibri 13 italic underline')
        self.c.create_text(250,240,text='WHAT IS THE HIDDEN GROUP',fill='steel blue',font = 'Chiller 20 bold',tags='title')
        self.c.create_text(495,495,text='Developed by SUTD 14F01 Group3',fill='black',anchor = 'se',font = 'Calibri 10')
        startBt = Button(self.window,text='START',bg='snow', fg='black',font='Calibri 10',activebackground='sky blue',relief=GROOVE,command=self.instruction)
        start = self.c.create_window(250,300, window=startBt, tags ='startbutton')

#LEVEL 1 SETTINGS
        self.classificationlist1 = [['circle'],['triangle'], ['square']]#OPTIONS TO CHOOSE FROM FOR LEVEL1
        self.x = self.randomizer(len(self.classificationlist1)-1)
        self.classification1 = self.classificationlist1[self.x]
#LEVEL 2 SETTINGS
        self.classificationlist2 = [['circle'],['triangle'], ['square'],['red'],['blue'],['Yellow']]#OPTIONS TO CHOOSE FROM FOR LEVEL2
        #['red', 'circle'], ['blue','circle'], ['Yellow','circle'], ['red','triangle'], ['blue','triangle'], ['Yellow', 'triangle'],['red', 'square'], ['blue', 'square'], ['Yellow', 'square']
        self.x = self.randomizer(len(self.classificationlist2)-1)
        self.classification2 = self.classificationlist2[self.x]
#LEVEL 3 SETTINGS
        self.classificationlist3 = [['red'],['blue'],['Yellow'],['even'], ['odd'],['circle'],['triangle'], ['square']]#OPTIONS TO CHOOSE FROM FOR LEVEL3
        #['red', 'circle'], ['blue','circle'], ['Yellow','circle'], ['red','triangle'], ['blue','triangle'], ['Yellow', 'triangle'],['red', 'square'], ['blue', 'square'], ['Yellow', 'square'], ['red', 'even'], ['red' ,'odd'], ['blue', 'even'], ['blue', 'odd'], ['Yellow', 'even'], ['Yellow', 'odd'], ['triangle' ,'even'], ['triangle', 'odd'], ['circle', 'even'], ['circle', 'odd'], ['square', 'even'], ['square', 'odd']
        self.x = self.randomizer(len(self.classificationlist3)-1)
        self.classification3 = self.classificationlist3[self.x]
        

        self.window.mainloop()
#Instruction page
    def instruction(self):
        self.c.delete(ALL)
        readyBt = Button(text='GO',bg='snow',activebackground='sky blue',relief=GROOVE,command=self.startlvl1)
        self.c.create_window(250,400,window=readyBt)
        self.c.create_text(250,100,fill='steel blue',text='INSTRUCTIONS',font='Chiller 20 bold',tags='titleInc')
        self.c.create_text(250,250,font='Calibri 12',text=' Different objects will show up on the screen.\n There will be an unknown classification standard each round.\n Press keyboard RIGHT if you think the object falls into the hidden group.\n Press keyboard DOWN for the next object.\n A point is rewarded if you are correct.\n Collect 5 points to proceed to the next level.\n A life is deducted for every wrong answer.\n You have 10 lives in total.\n\n Now, good luck! Click GO if you want to start.')
        


        
#LEVEL 1
    def startlvl1(self):
        self.winCount = 0
        self.loseCount = 0
        self.c.delete(ALL)
        self.c.create_text(250,50,text='LEVEL 1',font='Calibri 20 bold',fill='steel blue')
        restartBt = Button(text='RESTART',bg='snow',command=self.startlvl1)
        self.c.create_window(50,50,window = restartBt)
        self.createUI()#CALL FUNCTION TO CREATE STANDARDIZED UI
        self.lvl1shape()#DISPLAY SHAPES
    def lvl1shape(self):
        self.c.create_rectangle(200,200,300,300,fill='white',outline='snow',tags='bg')
        self.shapeslistlvl1 = [['circle'], ['square'], ['triangle']]
        self.y = self.randomizer(len(self.shapeslistlvl1)-1)#PICK SHAPE BY RANDOMIZER
        print 'shape: ' + str(self.shapeslistlvl1[self.y][0])
        print 'Classification: ' +str(self.classification1)
        print self.winCount,self.loseCount
        
        #RANDOM SHAPE GENERATOR
        if self.shapeslistlvl1[self.y][0] == 'circle':
            self.c.create_oval(225,225,275,275, fill = 'red',tags = 'shape')
        elif self.shapeslistlvl1[self.y][0] == 'square':
            self.c.create_rectangle(225,225,275,275, fill = 'red',tags = 'shape')
        elif self.shapeslistlvl1[self.y][0] == 'triangle':
            self.c.create_polygon(250,225,225,275,275,275, fill = 'red',tags = 'shape')

        self.c.bind('<Key>', self.keypress1)



#LEVEL 1 PRESSING OF KEY
    def keypress1(self,event):
        print event.keysym
        if self.winCount <5 and self.loseCount < 10:
            if event.keysym == "Right":
                self.c.delete('shape','bg')
                self.window.focus_set()
                if self.classification1 == self.shapeslistlvl1[self.y]:
                    print 'right'
                    self.winCount +=1
                    self.c.itemconfig('point%s'%str(self.winCount),fill='steel blue')#ADD POINT
                    self.c.create_text(250,250,text='You chose in the group.\nCORRECT!',tags = 'a')
                    if self.winCount == 5:
                        self.c.create_text(250,280, text='GROUP:%s'%str(self.classification1[0]))#DISPLAY CORRECT RESULT
    
                else:  
                    print 'right'
                    self.loseCount += 1
                    self.c.itemconfig('life%s'%str(self.loseCount),fill='snow')#MINUS LIFE
                    self.c.create_text(250,250,text='You chose in the group.\nWRONG!',tags = 'a')
    
                if self.winCount == 5:
                    self.after = self.window.after(2000,self.completed1)#CONDITION TO ENTER NEXT LEVEL(APPLICABLE TO ALL LEVELS)
                elif self.loseCount == 10:
                    self.after = self.window.after(2000,self.failed)#CONDITION TO FAIL(APPLICABLE TO ALL LEVELS)
                if self.winCount <= 4 and self.loseCount <= 9:
                    self.after = self.window.after(2000,self.reset1)
    
                    
            elif event.keysym =="Down":
                self.c.delete('shape','bg')
                self.window.focus_set()
                if self.classification1 != self.shapeslistlvl1[self.y]:
                    self.winCount +=1
                    self.c.itemconfig('point%s'%str(self.winCount),fill='steel blue')
                    self.c.create_text(250,250,text='You chose not in the group.\nCORRECT!',tags = 'a')
                    if self.winCount == 5:
                        self.c.create_text(250,280, text='GROUP:%s'%str(self.classification1[0]))
                
                else:  
                    self.loseCount +=1
                    self.c.itemconfig('life%s'%str(self.loseCount),fill='snow')
                    self.c.create_text(250,250,text='You chose not in the group.\nWRONG!',tags = 'a')
                if self.winCount == 5:
                    self.after = self.window.after(2000,self.completed1)
                elif self.loseCount == 10:
                    self.after = self.window.after(2000,self.failed)
                if self.winCount < 5 and self.loseCount < 10:
                    self.after = self.window.after(2000,self.reset1)
        
       
#LEVEL 2   
    def startlvl2(self):
        self.winCount = 0
        self.loseCount = 0
        self.c.delete(ALL)
        self.c.create_text(250,50,text='LEVEL 2',font='Calibri 20 bold',fill='steel blue')
        restartBt = Button(text='RESTART',bg='snow',command=self.startlvl2)
        self.c.create_window(50,50,window = restartBt)
        self.createUI()
        self.lvl2shape()
        
    def lvl2shape(self):
        self.c.create_rectangle(200,200,300,300,fill='white',outline='snow',tags='bg')
        self.shapeslistlvl2 = [['red', 'circle'], ['blue', 'circle'], ['Yellow', 'circle'], ['red', 'triangle'], ['blue','triangle'], ['Yellow', 'triangle'], ['red', 'square'], ['blue', 'square'], ['Yellow', 'square']]
        self.y = self.randomizer(len(self.shapeslistlvl2)-1)
        print 'shape: ' + str(self.shapeslistlvl2[self.y])
        print 'Classification: ' +str(self.classification2)
        print self.winCount
#CREATING CIRCLES
        if self.shapeslistlvl2[self.y][1] == 'circle':
            self.c.create_oval(225,225,275,275, fill = self.shapeslistlvl2[self.y][0],tags = 'shape')
#CREATING SQUARES
        if self.shapeslistlvl2[self.y][1] == 'square':
            self.c.create_rectangle(225,225,275,275, fill = self.shapeslistlvl2[self.y][0],tags = 'shape')
#CREATING TRIANGLES
        if self.shapeslistlvl2[self.y][1] == 'triangle':
            self.c.create_polygon(250,225,225,275,275,275, fill = self.shapeslistlvl2[self.y][0],tags = 'shape')

        self.c.bind('<Key>', self.keypress2)

#LEVEL 2 KEYPRESS       
    def keypress2(self,event):
        print event.keysym
        if self.winCount <5 and self.loseCount < 10:
            if event.keysym == "Right":
                self.c.delete('shape','bg')
                x = True
                #MATCHING CLASSIFICATION
                for i in range(len(self.classification2)):
                    if self.classification2[i] not in self.shapeslistlvl2[self.y]:
                        x = False
                if x == True:      
                    self.winCount +=1
                    self.c.itemconfig('point%s'%str(self.winCount),fill='steel blue')
                    self.c.create_text(250,250,text='You chose in the group.\nCORRECT!',tags = 'a')
                    if self.winCount == 5:
                        self.c.create_text(250,280, text='GROUP:%s'%str(self.classification2[0]))
                elif x == False:  
                    self.loseCount +=1
                    self.c.itemconfig('life%s'%str(self.loseCount),fill='snow')
                    self.c.create_text(250,250,text='You chose in the group.\nWRONG!',tags = 'a')
                if self.winCount == 5:
                    self.after = self.window.after(2000,self.completed2)
                if self.loseCount == 10:
                    self.after = self.window.after(2000,self.failed)
                if self.winCount < 5 and self.loseCount < 10:
                    self.after = self.window.after(2000,self.reset2) 
                    
            elif event.keysym =="Down":
                self.c.delete('shape','bg')
                x=True
                #MATCHING CLASSIFICATION
                for i in range(len(self.classification2)):
                    if self.classification2[i] not in self.shapeslistlvl2[self.y]:
                        x = False
                if x==False:
                    self.winCount +=1
                    self.c.itemconfig('point%s'%str(self.winCount),fill='steel blue')
                    self.c.create_text(250,250,text='You chose not in the group.\nCORRECT!',tags = 'a')
                    if self.winCount == 5:
                        self.c.create_text(250,280, text='GROUP:%s'%str(self.classification2[0]))
                elif x==True:  
                    self.loseCount +=1
                    self.c.itemconfig('life%s'%str(self.loseCount),fill='snow')
                    self.c.create_text(250,250,text='You chose not in the group.\nWRONG!',tags = 'a')
    
                if self.winCount == 5:
                    self.after = self.window.after(2000,self.completed2)
                if self.loseCount == 10:
                    self.after = self.window.after(2000,self.failed)
                if self.winCount < 5 and self.loseCount < 10:
                    self.after = self.window.after(2000,self.reset2) 
            
        
#LEVEL 3   
    def startlvl3(self):
        self.winCount = 0
        self.loseCount = 0
        self.c.delete(ALL) 
        self.c.create_text(250,50,text='LEVEL 3',font='Calibri 20 bold',fill='steel blue')
        restartBt = Button(text='RESTART',bg='snow',command=self.startlvl3)
        self.c.create_window(50,50,window = restartBt)
        self.createUI()
        self.lvl3shape()
        
    def lvl3shape(self):
        self.c.create_rectangle(200,200,300,300,fill='white',outline='snow',tags='bg')
        self.shapeslistlvl3 = [['red', 'circle', 'even'], ['red', 'circle', 'odd'], ['blue', 'circle', 'even'], ['blue', 'circle', 'odd'], ['Yellow', 'circle', 'even'], ['Yellow', 'circle' ,'odd'], ['red', 'triangle', 'even'], ['red', 'triangle', 'odd'], ['blue','triangle', 'even'], ['blue','triangle', 'odd'], ['Yellow', 'triangle', 'even'], ['Yellow', 'triangle', 'odd'], ['red', 'square', 'even'], ['red', 'square', 'odd'], ['blue', 'square', 'even'], ['blue', 'square', 'odd'], ['Yellow', 'square', 'even'], ['Yellow', 'square', 'odd']]
        self.y = self.randomizer(len(self.shapeslistlvl3)-1)
        print 'shape: ' + str(self.shapeslistlvl3[self.y])
        print 'Classification: ' +str(self.classification3)
        print self.winCount
#CREATING circleS
        if self.shapeslistlvl3[self.y][1] == 'circle':
            self.c.create_oval(225,225,275,275, fill =self.shapeslistlvl3[self.y][0],tags = 'shape')
            if self.shapeslistlvl3[self.y][2] == 'even':
                a = random.randrange(2,11,2)
            else:
                a = random.randrange(1,10,2)
            self.c.create_text(250,255,text=str(a),tags = 'number',fill='white')
#CREATING squareS
        if self.shapeslistlvl3[self.y][1] == 'square':
            self.c.create_rectangle(225,225,275,275, fill =self.shapeslistlvl3[self.y][0],tags = 'shape')
            if self.shapeslistlvl3[self.y][2] == 'even':
                a = random.randrange(2,11,2)
            else:
                a = random.randrange(1,10,2)
            self.c.create_text(250,255,text=str(a),tags = 'number',fill='white')
#CREATING triangleS
        if self.shapeslistlvl3[self.y][1] == 'triangle':
            self.c.create_polygon(250,225,225,275,275,275, fill = self.shapeslistlvl3[self.y][0],tags = 'shape')
            if self.shapeslistlvl3[self.y][2] == 'even':
                a = random.randrange(2,11,2)
            else:
                a = random.randrange(1,10,2)
            self.c.create_text(250,255,text=str(a),tags = 'number',fill='white')
       
        self.c.bind('<Key>', self.keypress3)

#LEVEL 3 KEYPRESS       
    def keypress3(self,event):
        print event.keysym
        if self.winCount <5 and self.loseCount < 10:
            if event.keysym == "Right":
                self.c.delete('shape')
                self.c.delete('number','bg')
                x = True
                for i in range(len(self.classification3)):
                    if self.classification3[i] not in self.shapeslistlvl3[self.y]:
                        x = False
                if x == True:      
                    self.winCount +=1
                    self.c.itemconfig('point%s'%str(self.winCount),fill='steel blue')
                    self.c.create_text(250,250,text='You chose in the group.\nCORRECT!',tags = 'a')
                    if self.winCount == 5:
                        self.c.create_text(250,280, text='GROUP:%s'%str(self.classification3[0]))
                elif x == False:  
                    self.loseCount +=1
                    self.c.itemconfig('life%s'%str(self.loseCount),fill='snow')
                    self.c.create_text(250,250,text='You chose in the group.\nWRONG!',tags = 'a')
                if self.winCount == 5:
                    self.after = self.window.after(2000,self.completed3)
                if self.loseCount == 10:
                    self.after = self.window.after(2000,self.failed)
                if self.winCount < 5 and self.loseCount < 10:
                    self.after = self.window.after(2000,self.reset3) 
                    
            elif event.keysym =="Down":
                self.c.delete('shape')
                self.c.delete('number','bg')
                x = True
                for i in range(len(self.classification3)):
                    if self.classification3[i] not in self.shapeslistlvl3[self.y]:
                        x = False
                if x==False:
                    self.winCount +=1
                    self.c.itemconfig('point%s'%str(self.winCount),fill='steel blue')




                    self.c.create_text(250,250,text='You chose not in the group.\nCORRECT!',tags = 'a')
                    if self.winCount == 5:
                        self.c.create_text(250,280, text='GROUP:%s'%str(self.classification3[0]))
                elif x==True:  
                    self.loseCount +=1
                    self.c.itemconfig('life%s'%str(self.loseCount),fill='snow')
                    self.c.create_text(250,250,text='You chose not in the group.\nWRONG!',tags = 'a')
    
                if self.winCount == 5:
                    self.after = self.window.after(2000,self.completed3)
                if self.loseCount == 10:
                    self.after = self.window.after(2000,self.failed)
                if self.winCount < 5 and self.loseCount < 10:
                    self.after = self.window.after(2000,self.reset3) 
                    
#RANDOM NUMBER GENERATOR
    def randomizer(self,inp):
        return random.randint(0,inp)

#UI CREATOR
    def createUI(self):
        #LIFE COUNTER
        self.c.create_text(380,20,text='LIFE REMAINING:',anchor='nw',font='Calibri 10',fill='dim gray')
        self.c.create_oval(380,40,390,50,fill='LightPink1',tags='life1')
        self.c.create_oval(400,40,410,50,fill='LightPink1',tags='life2')
        self.c.create_oval(420,40,430,50,fill='LightPink1',tags='life3')
        self.c.create_oval(440,40,450,50,fill='LightPink1',tags='life4')
        self.c.create_oval(460,40,470,50,fill='LightPink1',tags='life5')
        self.c.create_oval(380,60,390,70,fill='LightPink1',tags='life6')
        self.c.create_oval(400,60,410,70,fill='LightPink1',tags='life7')
        self.c.create_oval(420,60,430,70,fill='LightPink1',tags='life8')
        self.c.create_oval(440,60,450,70,fill='LightPink1',tags='life9')
        self.c.create_oval(460,60,470,70,fill='LightPink1',tags='life10')
        #INSTRUCTIONS
        self.c.create_polygon(110,220,130,220,130,270,140,270,120,300,100,270,110,270,fill='light steel blue')
        self.c.create_polygon(350,240,400,240,400,230,430,250,400,270,400,260,350,260,fill='light steel blue')
        self.c.create_text(120,180,text='NOT IN THE GROUP',fill='light steel blue',font='Calibri 12')
        self.c.create_text(400,180,text='IN THE GROUP',fill='light steel blue',font='Calibri 12')
        #POINTS ACCUMULATION BAR
        self.c.create_rectangle(105,400,155,410,fill='snow',tags='point1')
        self.c.create_rectangle(165,400,215,410,fill='snow',tags='point2')
        self.c.create_rectangle(225,400,275,410,fill='snow',tags='point3')
        self.c.create_rectangle(285,400,335,410,fill='snow',tags='point4')
        self.c.create_rectangle(345,400,395,410,fill='snow',tags='point5')
        self.c.create_text(450,405,text='TO NEXT LEVEL',fill='steel blue',font='Calibri 10')

#RESET FUNCTIONS FOR 3 LEVELS
    def reset1(self):
        self.c.focus_set()
        self.c.delete('a')
        self.lvl1shape()
        self.window.after_cancel(self.after)   
        
    def reset2(self):
        self.c.focus_set()
        self.c.delete('a')
        self.lvl2shape()
        self.window.after_cancel(self.after)  
        
    def reset3(self):
        self.c.focus_set()
        self.c.delete('a')
        self.lvl3shape()
        self.window.after_cancel(self.after) 
         
#COMPLETION PAGES
    def completed1(self):
        self.c.delete(ALL)
        self.c.update()
        self.c.create_text(250,220,text='CONGRATULATIONS!',fill='steel blue',font='Chiller 15 bold')
        self.c.create_text(250,250,text='You have completed level 1!',fill='black',font='Calibri 15')
        self.c.update()
        time.sleep(1)
        startbutton = Button(self.c,text = "START LEVEL 2", activebackground='sky blue',relief=GROOVE,command = self.startlvl2)
        self.c.create_window(250, 300,window=startbutton, tags ='startbutton')
        self.c.focus_set()


    def completed2(self):
        self.c.delete(ALL)
        self.c.create_text(250,220,text='CONGRATULATIONS!',fill='steel blue',font='Chiller 15 bold')
        self.c.create_text(250,250,text='You have completed level 2!',fill='black',font='Calibri 15')
        self.c.update()
        time.sleep(1)
        startbutton = Button(self.c,text = "START LEVEL 3",activebackground='sky blue',relief=GROOVE, command = self.startlvl3)
        start = self.c.create_window(250, 300, window=startbutton, tags ='startbutton')
        self.c.focus_set()

    def completed3(self):
        self.c.delete(ALL)
        self.c.create_text(250,220,text='CONGRATULATIONS!',fill='steel blue',font='Chiller 15 bold')
        self.c.create_text(250,250,text='YOU HAVE WON THE GAME!',fill='steel blue',font='Chiller 15 bold')
        self.c.create_text(250,300,text='Hope you enjoyed it.',fill='black',font ='Calibri 10')
        startbutton = Button(self.c,text = "RESTART",activebackground='sky blue',relief=GROOVE, command = self.startlvl1)
        start = self.c.create_window(250, 400, window=startbutton, tags ='startbutton')
        self.c.create_text(495,495,text='Developed by SUTD 14F01 Group3',fill='black',anchor = 'se',font = 'Calibri 10')
        self.c.focus_set()

#FAILURE PAGE      
    def failed(self):
        self.c.delete(ALL)
        self.winCount = 0
        self.loseCount = 0
        self.c.create_text(250,220,text='SORRY YOU HAVE FAILED THIS TRIAL.\nPLEASE TRY AGAIN.',fill='black',font='Chiller 15')
        time.sleep(1)
        startbutton = Button(self.c,text = "RESTART", command = self.startlvl1)
        startbutton.configure(width = 10, activebackground='sky blue',relief=GROOVE)
        start = self.c.create_window(250,280,window=startbutton, tags ='startbutton')
        self.c.focus_set()

        
        
a = game()

        
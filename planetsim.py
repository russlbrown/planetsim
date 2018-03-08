from graphics import *
import random, time, sys

def main(planets, massMax):
    maxDesiredAccel = 10**10 #maximum acceleration allowed before calculation accuracy is ramped up. try 1
    dt=0.001				#desired time per iteration in seconds
    G=300000.3    			#Force calibration constant. try 0.03
    rr=1      			#Rebound Ratio
    xMax,yMax=900,600 	#window size
    vMax=1.5     			#Maximum initial velocity in either the x or y direction. try 0.1
    #massMax=500		#Maximum mass. Try 125
    #planets=10			#Number of planets
    stars=10			#Number of stars
                                #good defaults on mac: G=0.03, vmax=0.1, massMax=100
    win=GraphWin("PlanetSim by RLB", xMax, yMax, False)
    win.setBackground(color_rgb(0,0,0))
    win.update();

    #Generate Stars
    for i in range(stars):
        x=random.randrange(1,xMax)
        y=random.randrange(1,yMax)
        star=Circle(Point(x,y),0)
        star.draw(win)
        c=random.randrange(10,255)
        star.setOutline(color_rgb(c,c,c))

    while True:
        #Populate planets and their info
        planet=generatePlanets(planets,massMax,xMax,yMax,vMax)
        #planet.append({'radius':4,"mass":50,"x":350.0,"y":350.0,"oldX":0.0,'oldY':0.0,"dx":0.08,"dy":-0.08,"r":255,"g":0,"b":0,"ax":0.0,"ay":0.0})
        #planet.append({'radius':4,"mass":50,"x":250.0,"y":340.0,"oldX":0.0,'oldY':0.0,"dx":-0.04,"dy":0.04,"r":0,"g":255,"b":0,"ax":0.0,"ay":0.0})
        #planet.append({'radius':4,"mass":50,"x":450.0,"y":340.0,"oldX":0.0,'oldY':0.0,"dx":-0.04,"dy":0.04,"r":0,"g":0,"b":255,"ax":0.0,"ay":0.0})
        
        #draw planets
        for i in range(len(planet)):
            planet[i]['image']=Circle(Point(planet[i]['x'],planet[i]['y']),planet[i]['radius'])
            planet[i]['image'].draw(win)
            planet[i]['image'].setFill(color_rgb(planet[i]['r'],planet[i]['g'],planet[i]['b']))
            planet[i]['image'].setOutline(color_rgb((planet[i]['r'] + 255) // 2, (planet[i]['g'] + 255) // 2,
                                                    (planet[i]['b'] + 255) // 2))
        win.update()
        
        #Main Loop
        while True:
            start() #start timer
            
            #clear accel variables, then calculate total acceleration of each planet
            for i in range(len(planet)):
                planet[i]['ax']=0.0
                planet[i]['ay']=0.0
            largestAccel=0.0
            accelList=[]
            
            for i in range(len(planet)):
                for j in range(i+1,len(planet)):
                    distance=getDistance(planet[i],planet[j])
                    force=getGForce(planet[i],planet[j],distance,G)
                    
                    #calculate acceleration of each planet
                    planet[i]['ax']=planet[i]['ax']+force['x']/planet[i]['mass']
                    planet[i]['ay']=planet[i]['ay']+force['y']/planet[i]['mass']
                    planet[j]['ax']=planet[j]['ax']-1*force['x']/planet[j]['mass']
                    planet[j]['ay']=planet[j]['ay']-1*force['y']/planet[j]['mass']
            
            #Get Maximum acceleration and compare it to max allowed		
            for i in range(len(planet)):
                accelList.append(accelMag(planet[i]))
            largestAccel = max(accelList)
            
            if largestAccel>maxDesiredAccel:
                tempdt = maxDesiredAccel*dt/largestAccel
                print(f"LargestAccel > maxDesiredAccel. Slowing things down")
                #slow everything down by factor tempdt
                for i in range(len(planet)):
                    planet[i]['dx']=planet[i]['dx']*tempdt
                    planet[i]['dy']=planet[i]['dy']*tempdt
            else:
                tempdt=dt;
                    
            #Calculate new velocities and positions
            for i in range(len(planet)):
                planet[i]['dx']=planet[i]['dx']+0.5*planet[i]['ax']*(tempdt**2);
                planet[i]['dy']=planet[i]['dy']+0.5*planet[i]['ay']*(tempdt**2);
                planet[i]['x']=planet[i]['x']+planet[i]['dx'];
                planet[i]['y']=planet[i]['y']+planet[i]['dy'];
            for i in range(len(planet)):
                planet[i]['image'].move(planet[i]['dx'],planet[i]['dy']);
                    
            #speed everything up to regular speed
            if largestAccel>maxDesiredAccel:
                for i in range(len(planet)):
                    planet[i]['dx']=planet[i]['dx']/tempdt
                    planet[i]['dy']=planet[i]['dy']/tempdt
            
            #detect collisions with walls and rebound
            for i in range(len(planet)):
                if planet[i]['x']>xMax-planet[i]['radius']:
                    planet[i]['dx']=-1*abs(planet[i]['dx']*rr)
                if planet[i]['y']>yMax-planet[i]['radius']:
                    planet[i]['dy']=-1*abs(planet[i]['dy']*rr)
                if planet[i]['x']<1+planet[i]['radius']:
                    planet[i]['dx']=abs(planet[i]['dx']*rr)
                if planet[i]['y']<1+planet[i]['radius']:
                    planet[i]['dy']=abs(planet[i]['dy']*rr)
            
            #detect interplanetary collisions
            collisionBtw=[];
            for i in range(len(planet)):
                for j in range(i+1,len(planet)):
                    distance=getDistance(planet[i],planet[j])
                    if distance<planet[i]['radius']+planet[j]['radius']:
                        collisionBtw.append([i,j]);
                    
            for col in range(len(collisionBtw)):
                i,j=collisionBtw[col][0],collisionBtw[col][1]
                energy={i:getEnergy(planet[i]),j:getEnergy(planet[j])}
                combinedMass=1.0*(planet[i]['mass']+planet[j]['mass'])
                if energy[i]>energy[j]:
                    winner,loser=i,j;
                else:
                    winner,loser=j,i;
                planet[winner]['x']=planet[winner]['x'] + ((planet[loser]['x']-planet[winner]['x'])*planet[loser]['mass']/combinedMass)
                planet[winner]['y']=planet[winner]['y'] + ((planet[loser]['y']-planet[winner]['y'])*planet[loser]['mass']/combinedMass)
                planet[winner]['dx']=(planet[winner]['dx']*planet[winner]['mass']+planet[loser]['dx']*planet[loser]['mass'])/combinedMass
                planet[winner]['dy']=(planet[winner]['dy']*planet[winner]['mass']+planet[loser]['dy']*planet[loser]['mass'])/combinedMass
                planet[winner]['mass']=combinedMass
                planet[winner]['radius']=int(abs(combinedMass)**(1.0/3))
                                        
                planet[winner]['image'].undraw()
                planet[loser]['image'].undraw()
                                                                                
                planet[winner]['image']=Circle(Point(planet[winner]['x'],planet[winner]['y']),planet[winner]['radius'])
                planet[winner]['image'].draw(win)
                planet[winner]['image'].setFill(color_rgb(planet[winner]['r'],planet[winner]['g'],planet[winner]['b']))
                planet[winner]['image'].setOutline(color_rgb((planet[winner]['r']+255)//2,(planet[winner]['g']+255)//2,(planet[winner]['b']+255)//2))
        
                del planet[loser];
                    
            finish()
            
            calcDelay=duration()
            if calcDelay>tempdt/10:
                calcDelay=0
            
            time.sleep((tempdt/5)-calcDelay)	
            win.update()
    
            if len(planet) < 2:
                time.sleep(0.0001)
                win.update()
                time.sleep(3)
                input("End of Simulation")
                planet[0]['image'].undraw()
                win.close()
                sys.exit(0)
    
    win.getMouse()
    win.close()
    import sys
    sys.exit(0)

def generatePlanets(planets,massMax,xMax,yMax,vMax):
    planet=[]
    for i in range(planets):
        mass=random.randrange(1,massMax)
        radius=int(abs(mass)**(1.0/3))
        x=random.randrange(10,xMax-10)
        y=random.randrange(10,yMax-10)
        dx=random.uniform(-vMax,vMax)
        dy=random.uniform(-vMax,vMax)
        r=random.randrange(0,255)
        g=random.randrange(0,255)
        b=random.randrange(0,255)
        #image=Circle(Point(x,y),radius)
        planet.append({'radius':radius,"mass":mass,"x":x,"y":y,"oldX":0.0,'oldY':0.0,"dx":dx,"dy":dy,"r":r,"g":g,"b":b,"ax":0.0,"ay":0.0})
    return planet

def getGForce(planet1,planet2,distance,G):
    acceleration={'x':G*planet1["mass"]*(planet2['mass']/distance**3)*(planet2['x']-planet1['x']),
	'y':G*planet1["mass"]*(planet2['mass']/distance**3)*(planet2['y']-planet1['y'])}
    return acceleration

def accelMag(planet):
    accelMag=(planet['ax']**2+planet['ay']**2)**0.5
    return accelMag
	
def getDistance(planet1,planet2):
    distance=(((planet2['x']-planet1['x'])**2) + ((planet2['y']-planet1['y'])**2))**0.5
    return distance
	
def getEnergy(planet):
    #energy=0.5*planet['mass']*(planet['dx']**2+planet['dy']**2)
    momentum=planet['mass']*(planet['dx']**2+planet['dy']**2)**(0.5)
    return momentum
	
if sys.platform == "win32":
    timer = time.clock
else:
    timer=time.time

def start():
    global t0
    t0 = timer()
	
def finish():
    global t1
    t1=timer()

def duration():
    return round((t1 - t0),5)

def setup():
    """Get user input for the simulation"""
    while True:

        number_of_planets = input("Enter number of planets (2-20): ")
        max_mass = input ("Enter maximum planet mass (1-1000): ")

        try:
            number_of_planets = int(number_of_planets)
            max_mass = int(max_mass)
        except:
            print(f"Invalid input. Try again.")
            continue
            
        main(number_of_planets, max_mass)


setup()

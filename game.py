

# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 12:35:30 2023

@author: gdawe2
"""

import os
from importlib import reload
import copy
import arcade
import math
import driver
import ship
import stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from params import GameParameters,Var1Pars

SCREEN_WIDTH = 180
SCREEN_HEIGHT = 128
SCREEN_TITLE = "PID"
TIME_FACTOR = 0.0166

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)
        self.ct = 0

        #self.parameters = driver.DriverParameters(1,60,0.0025,0.2)
        self.switch_time = 0

    def setup(self):

        self.ship = ship.Ship()
        self.stats = stats.Stats(ship=self.ship)
        self.driver = driver.Driver(ship=self.ship)

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()
        self.ship.draw()
        self.stats.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        # Kp=1
        # Kd=60
        # Ki=0.0025
        # Integraal_Factor=0.2



        self.switch_time += delta_time
        if self.switch_time > TIME_FACTOR:
            self.switch_time -= TIME_FACTOR
            self.tick(self.parameters)

        self.ship = self.ship.reload()
        self.stats = self.stats.reload(ship=self.ship)
        self.driver = self.driver.reload(ship=self.ship)
        # TODO: we have to tell stats about the ship, esp. when it was reloaded

    def tick(self, parameters):
        self.ct += 1

        thrust = self.driver.tick(self.ct,parameters)
        self.ship.control = thrust
        self.ship.tick(self.ct,parameters)
        #self.stats.tick(self.ct, p, d, i)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == 65361:  # left
            self.ship.thrust += -1
        elif key == 65363:  # right
            self.ship.thrust += 1
        elif key == 113:  # Q
            self.close()
        elif key == 114:  # R
            self.ship.reset()
            self.stats.ship = self.ship
            self.driver.ship = self.ship
        elif key == 115:  # S
            self.ship.star_wind = 3 - self.ship.star_wind
        else:
            print("key press", key)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == 65361:  # left
            self.ship.thrust += 1
        elif key == 65363:  # right
            self.ship.thrust += -1

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        # print("mouse motion", x, y, delta_x, delta_y)
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        print("mouse press", x, y, button)
        # self.close()
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        print("mouse release", x, y, button)
        pass
    
    def perform_1_iteration(self,parameters):
        """
        Play 1 iteration and plot x,v and t as timeseries
        """
        self.tick(parameters)
        self.ship.xAll.append(self.ship.x)
        self.ship.vAll.append(self.ship.speed)
        self.ship.t += TIME_FACTOR
        self.ship.tAll.append(self.ship.t)

    def reach_equilibrium_daan(self):
      " Step 1: Check if direction turns within w. It uses a running mean of 10 timesteps"
      if len(self.ship.xAll) > 15:
          dx_last10_0 = self.ship.xAll[-10:]
          dx_last10_1 = self.ship.xAll[0:-1][-10:]
          dx1 = np.mean(np.diff(dx_last10_0))
          dx2 = np.mean(np.diff(dx_last10_1))         
                
          if dx1 * dx2 < (10**-13) and abs(self.ship.x) < 0.05:
                self.ship.EQ = 1      
                      
          if self.ship.EQ == 1:               
            " Step 2: Find last timestep that x crosses a boundary of w"
            binnenW = np.where(np.abs(np.array(self.ship.xAll))< .05)[0] 
            if(binnenW.size>0):
                binnenW_diff = np.diff(binnenW)
                if(binnenW_diff.size>0):
                    if np.max(binnenW_diff) > 1:
                        t_index = binnenW[np.where(binnenW_diff > 1)[0][-1]+1]
                    else:
                        t_index = binnenW[0]    
            
                    self.ship.tEQ = self.ship.tAll[t_index]                
                    print(self.ship.tEQ)


    def reach_equilibrium(self):
        " Step 1: Check if direction turns within w. It uses a running mean of 10 timesteps"
        # print(len(self.ship.xAll))
      
        eqWaarde=999
        index=0
        for i in range(len(self.ship.xAll)-1,0,-1):
            if(abs(self.ship.xAll[i]) < 0.05):
                eqWaarde=self.ship.xAll[i]
            else:
                index=i
                break

        if(eqWaarde!=999):
            self.ship.EQ = 1
            self.ship.tEQ = self.ship.tAll[index]                

        # if len(self.ship.xAll) > 15:
        #   dx_last10_0 = self.ship.xAll[-10:]
        #   dx_last10_1 = self.ship.xAll[0:-1][-10:]
        #   dx1 = np.mean(np.diff(dx_last10_0))
        #   dx2 = np.mean(np.diff(dx_last10_1))         
                
        #   if dx1 * dx2 < (10**-13) and abs(self.ship.x) < 0.05:
        #         self.ship.EQ = 1      
                      
        #   if self.ship.EQ == 1:               
        #     " Step 2: Find last timestep that x crosses a boundary of w"
        #     binnenW = np.where(np.abs(np.array(self.ship.xAll))< .05)[0] 
        #     if(binnenW.size>0):
        #         binnenW_diff = np.diff(binnenW)
        #         if(binnenW_diff.size>0):
        #             if np.max(binnenW_diff) > 1:
        #                 t_index = binnenW[np.where(binnenW_diff > 1)[0][-1]+1]
        #             else:
        #                 t_index = binnenW[0]    
            
        #             self.ship.tEQ = self.ship.tAll[t_index]                

                

def main():
    """
    Set-up game, and functions to run and reset game
    """

    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()

    def run(game,par : GameParameters):
        " Stop run if equilibrium has reached, or after 20000 iterations "
        i = 0
        game.parameters = par
        maxIter=20000
        # if game.parameters.sigma>0:
        #     maxIter=5000

        while ((game.ship.EQ < 1 or game.parameters.sigma>0) and i < maxIter):
            i += 1        
            game.perform_1_iteration(game.parameters)

        game.reach_equilibrium()
        gs = game.ship
        timeseries = pd.DataFrame({'time':gs.tAll,'x':gs.xAll,'v':list(np.array(gs.vAll) / TIME_FACTOR)})
        if type(gs.tEQ) == float:
            return [timeseries,gs.tEQ]
        else:
            return [timeseries,math.nan]   

    def reset(game):
        game.ship.reset()
        game.driver.last_x = 0
        game.driver.i = 0   

    def fig_basis(ts,tEQ,par,volgnummer):   
        "Plot random runs"
        fs = 55
        fig = plt.figure(figsize=(27.5,13.5))
        if(par.sigma==0):
            ax1 = fig.add_axes([.12,.15, .85, .82])            
        else:
            ax1 = fig.add_axes([.12,.15, .85, .72])            
        ax1.plot(ts['time'],ts['x'],label='x-position',linewidth=3)
        ax1.plot(ts['time'],ts['v'],label='v-speed',linewidth=3)  
        ax1.plot([0,ts['time'].iloc[-1]],[0,0],label='Centre',linestyle='--',color='black',linewidth=3)
        if type(tEQ) == float:
            ax1.plot([tEQ,tEQ],[-1,1],label='Centre reached (5%)',linewidth=3)    
        ax1.set_xlabel('Time',fontsize=fs)
        ax1.set_ylabel('x and v',fontsize=fs)
        ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        ax1.legend(fontsize=fs-10)   
        if np.isnan(tEQ):
            ax1.set_xlim(0,ts['time'].iloc[-1])
        else:
            ax1.set_xlim(0,tEQ+2)

        if(par.sigma!=0):
            ax1.set_xlim(0,330)
            if(par.sigma<0.0027):
                ax1.set_xlim(0,50)

        ax1.grid()
        if(par.sigma==0):
            filenaam="figuren\\basis {0}.png".format(volgnummer)
        else:
            filenaam="figuren\\gaussian noise {0}.png".format(volgnummer)
            ax1.set_title('Sigma: {0}'.format(par.sigma),fontsize=fs)  

        if os.path.exists(filenaam):
            os.remove(filenaam)
        fig.savefig(filenaam)
        plt.close(fig)

    def fig_xt_change_1par_refactor(ts,vals,par,ncol,len_linrange):
        "x-t graphs to see what happens"
        fs = 55
        fig = plt.figure(figsize=(27.5,13.5))
        ax1 = fig.add_axes([.12,.15, .83, .72])             
        for ii in np.arange(0,len(ts)):
            ax1.plot(ts[ii]['time'],ts[ii]['x'],label=par+' = '+str(np.round(vals[ii],3)))
        ax1.set_title('Varying '+par,fontsize=fs)   
        ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        ax1.set_xlabel('time',fontsize=fs)
        ax1.set_ylabel('x',fontsize=fs)
        ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        ax1.grid()
        ax1.set_ylim(-2,2)
        ax1.set_xlim(0,20)
        ax1.legend(fontsize=fs,ncol=int(np.round(len_linrange/ncol)),loc='lower center',bbox_to_anchor = (.5,-.35)) #todo als parameter meegeven?
        fig.savefig("figuren\\xt 1 par {0}".format(par))
        plt.close(fig)        
    
    def fig_change_1par(x,y,par,sigma):   
        fs = 55
        fig = plt.figure(figsize=(27.5,13.5))
        ax1 = fig.add_axes([.12,.15, .83, .72])             
        ax1.plot(x,y,linewidth=3)
        ax1.set_title('Varying {0} - sigma={1}'.format(par,sigma),fontsize=fs)   
        ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        ax1.set_xlabel(par,fontsize=fs)
        ax1.set_ylabel('time',fontsize=fs)
        if par == 'Ki':
            ax1.tick_params(axis='x',labelsize=fs-10)
        else:
            ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        ax1.grid()
        if sigma==0:
            ax1.set_ylim(0,30)
        else:
            ax1.set_ylim(0,60)

        fig.savefig("figuren\\1 par {0} sigma {1}".format(par,str(sigma).replace('.',',')))
        plt.close(fig)
            
    def fig_change_2par(x,y,z,par1,par2,sigma): 
        Y,X = np.meshgrid(y,x)
        fs = 55
        fig = plt.figure(figsize=(27.5,13.5))
        ax1 = fig.add_axes([.12,.15, .83, .72])            
        cax = ax1.pcolor(X,Y,z,cmap='hot_r',vmin=0,vmax=20)
        ax1.set_title('Varying {0} and  {1} - sigma: {2}'.format(par1,par2,sigma),fontsize=fs)   
        ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        ax1.set_xlabel(par1,fontsize=fs)
        ax1.set_ylabel(par2,fontsize=fs)
        ax1.tick_params(axis='x',labelsize=fs)
        ax1.tick_params(axis='y',labelsize=fs)
        cbar = fig.colorbar(cax)
        cbar.ax.tick_params(labelsize=fs)
        cbar.ax.set_ylabel('time until equilibrium',fontsize=fs)
        fig.savefig("figuren\\2 par {0} en {1} sigma {2}".format(par1,par2,str(sigma).replace('.',',')))
        plt.close(fig)

    def runVraag2():
        """
        Question 2: Manually adapt parameters
        """
        print('Run and plot some random runs')
        pars=[GameParameters(1,60,0.0025,0.2),GameParameters(1,0,0,0.2),GameParameters(1,60,0,0),GameParameters(0.6,60,0.0025,0.2),GameParameters(5,200,0.0005,0.1),GameParameters(1,60,1,0.2)]
        iter=1
        for par in pars:
            spel=run(game,par)
            reset(game)
            fig_basis(spel[0],spel[1],par,iter)
            iter+=1

    def runVraag5a(sigma=0):
        """
        Question 5a: tEQ as function of 1 parameter
        """
        print('Run and plot 1 varying parameter')
        
        var1pars=[Var1Pars(0,6,31,'Kp'),Var1Pars(0,240,31,'Kd'),Var1Pars(0.0005,0.02,28,'Ki'),Var1Pars(0.04,0.4,28,'Kint')]
        pars=GameParameters(1,60,0.0025,0.2,sigma)
      
        for var1 in var1pars:
            linrange = np.linspace(var1.start,var1.stop,var1.num)
            tEQ = [math.nan] * len(linrange)
            SpelAll = [math.nan] * len(linrange)
            parcopy=copy.deepcopy(pars)
            for ii in np.arange(0,len(linrange)):
                if var1.var=='Kp':
                    parcopy.p_factor=linrange[ii]
                elif var1.var=='Kd':
                    parcopy.d_factor=linrange[ii]
                elif var1.var=='Ki':
                    parcopy.i_factor=linrange[ii]
                elif var1.var=='Kint':
                    parcopy.i_weight=linrange[ii]
                spel = run(game,parcopy)
                SpelAll[ii] = spel[0]
                if type(spel[1]) == float:
                    tEQ[ii] = spel[1] 
                reset(game)
            
            fig_xt_change_1par_refactor(SpelAll,linrange,var1.var,4,len(linrange))
            fig_change_1par(linrange,tEQ,var1.var,sigma)             
       
    def runVraag5b(sigma=0):
        """
        Question 5b: tEQ as function of 2 parameters
        """
        print('Run and plot 2 varying parameters: 1/6')

        resolutieFactor=6
            # " Varying Kp"
        p_range = np.linspace(0,6,31*resolutieFactor)
        d_range = np.linspace(0,240,31*resolutieFactor)
        i_range = np.linspace(0.0005,0.02,28*resolutieFactor)
        int_range = np.linspace(0.04,0.4,28*resolutieFactor)
    
        p_d_tEQ = np.empty((len(p_range),len(d_range)))*np.nan
        for ii in np.arange(0,len(p_range)):
            for jj in np.arange(0,len(d_range)):
                print("ii {0}: jj {1}".format(ii,jj))
                Spel0 = run(game,GameParameters(p_range[ii],d_range[jj],0.0025,0.2,sigma))
                if type(Spel0[1]) == float:
                    p_d_tEQ[ii,jj] = Spel0[1]
                reset(game)

        fig_change_2par(p_range,d_range,p_d_tEQ,'Kp','Kd',sigma)
                
        print('Run and plot 2 varying parameters: 2/6')
        p_i_tEQ = np.empty((len(p_range),len(i_range)))*np.nan
        for ii in np.arange(0,len(p_range)):
            print(ii)
            for jj in np.arange(0,len(i_range)):
                print(str(ii),str(jj))
                Spel0 = run(game,GameParameters(p_range[ii],60,i_range[jj],0.2,sigma))
                if type(Spel0[1]) == float:
                    p_i_tEQ[ii,jj] = Spel0[1]
                reset(game)
        
        fig_change_2par(p_range,i_range,p_i_tEQ,'Kp','Ki',sigma)

        print('Run and plot 2 varying parameters: 3/6')
        p_int_tEQ = np.empty((len(p_range),len(int_range)))*np.nan
        for ii in np.arange(0,len(p_range)):
            for jj in np.arange(0,len(int_range)):
                print(str(ii),str(jj))
                Spel0 = run(game,GameParameters(p_range[ii],60,0.0025,int_range[jj],sigma))
                if type(Spel0[1]) == float:
                    p_int_tEQ[ii,jj] = Spel0[1]
                reset(game)

        fig_change_2par(p_range,int_range,p_int_tEQ,'Kp','Kint',sigma)
        
        print('Run and plot 2 varying parameters: 4/6')
        d_i_tEQ = np.empty((len(d_range),len(i_range)))*np.nan
        for ii in np.arange(0,len(d_range)):
            for jj in np.arange(0,len(i_range)):
                print(str(ii),str(jj))
                Spel0 = run(game,GameParameters(1,d_range[ii],i_range[jj],0.2,sigma))
                if type(Spel0[1]) == float:
                    d_i_tEQ[ii,jj] = Spel0[1]
                reset(game)
                
        fig_change_2par(d_range,i_range,d_i_tEQ,'Kd','Ki',sigma)

        print('Run and plot 2 varying parameters: 5/6')
        d_int_tEQ = np.empty((len(d_range),len(int_range)))*np.nan
        for ii in np.arange(0,len(d_range)):
            for jj in np.arange(0,len(int_range)):
                print(str(ii),str(jj))
                Spel0 = run(game,GameParameters(1,d_range[ii],0.0025,int_range[jj],sigma))
                if type(Spel0[1]) == float:
                    d_int_tEQ[ii,jj] = Spel0[1]
                reset(game)

        fig_change_2par(d_range,int_range,d_int_tEQ,'Kd','Kint',sigma)

        print('Run and plot 2 varying parameters: 6/6')
        i_int_tEQ = np.empty((len(i_range),len(int_range)))*np.nan
        for ii in np.arange(0,len(i_range)):
            for jj in np.arange(0,len(int_range)):
                print(str(ii),str(jj))
                Spel0 = run(game,GameParameters(1,60,i_range[ii],int_range[jj],sigma))
                if type(Spel0[1]) == float:
                    i_int_tEQ[ii,jj] = Spel0[1]
                reset(game)

        fig_change_2par(i_range,int_range,i_int_tEQ,'Ki','Kint',sigma)

    def runVraag6():
        """
        Question 6: add random noise to spaceship position 
        """
        print('Run and plot some runs with random Gaussian noise')
        for iteller in range(1,31) :
            par=GameParameters(1,60,0.0025,0.2,round(math.log10(1+iteller/1000),4))
            spel=run(game,par)
            reset(game)
            fig_basis(spel[0],spel[1],par,iteller)

    if(not os.path.exists("figuren")):
        os.mkdir("figuren")

    runVraag2()
    runVraag5a(0)
    runVraag5a(0.0025)
    runVraag5b(0)
    runVraag5b(0.0025)
    runVraag6()

if __name__ == "__main__":
    main()

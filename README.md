# Introduction

This project is an elaboration of an assignment from the Open University, with the aim of investigating the tuning of parameters for a PID controller in a structured way.
We have taken J. Spielmann's PID controller (https://gitlab.com/jspielmann/shippid/) as a starting point.


# Simulation

In `params.py` we defined a class GameParameters which can contain al the varied parameters

class GameParameters:
      def __init__(self, p_factor,d_factor,i_factor,i_weight,sigma=0.0):
          self.p_factor=p_factor
          self.d_factor=d_factor
          self.i_factor=i_factor
          self.i_weight=i_weight
          self.sigma=sigma

We use these parameters in the altered Driver class (`driver.py`), to perform a simulation-iteration with application of these parameters.

    def tick(self, ct, parameters : GameParameters):
        Kp=parameters.p_factor
        Kd=parameters.d_factor
        Ki=parameters.i_factor
        Integraal_Factor=parameters.i_weight

        derivative = self.ship.x - self.last_x
        self.last_x = self.ship.x
        self.i = self.i + Integraal_Factor * self.ship.x
        return -5*(Kp*self.ship.x+Kd * derivative+Ki * self.i)

The Driver.tick function is called from MyGame.tick (`game.py`) which we changed to just run the simulation

    def tick(self, parameters):
        self.ct += 1

        thrust = self.driver.tick(self.ct,parameters)
        self.ship.control = thrust
        self.ship.tick(self.ct,parameters)

This function is called in on_update, which we changed to pass the parameters

You will notice that we also pass the parameters to ship.tick. This is only used for applying the noise (`ship.py`):

        if(parameters.sigma!=0): 
            offset=random.gauss(0,parameters.sigma)
            self.x +=offset

In `game.py` we also updated the run-function, to allow for 20000 iterations, capturing the results in a timeseries array and to check if and when the simulation has reached equilibrium.

    def run(game,par : GameParameters):
        " Stop run if equilibrium has reached, or after 20000 iterations "
        i = 0
        game.parameters = par
        maxIter=20000

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

The data for the timeseries is declared in the __init__ function of `ship.py` 

            self.xAll = [-1]
            self.vAll = [0]
            self.t = 0
            self.tAll = [0]
            self.EQ = 0
            self.tEQ = []

In `game.py` we build a function to perform one iteration of the simulation. Here we also capture the relevant data in the timeseries arrays

    def perform_1_iteration(self,parameters):
        """
        Play 1 iteration and plot x,v and t as timeseries
        """
        self.tick(parameters)
        self.ship.xAll.append(self.ship.x)
        self.ship.vAll.append(self.ship.speed)
        self.ship.t += TIME_FACTOR
        self.ship.tAll.append(self.ship.t)

Here we also defined a function to determine if an equilibrium has been reached, simply by checking if from some point in the timeseries the position doesn't deviate 5% from the targetvalue of 0. 

    def reach_equilibrium(self):
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

# Reporting

For running the simulations, we build specific functions in `game.py`

## Task 2

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


For this task, we defined GameParameters for a number of parameters which we chose. We run the simulation with these parameters, capture the data in spel, and pass this to the fig_basis function.

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

## Task 5

Here we used the matplotlib to plot the results. 

For task 5 we created the following functions:

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


Here we use numpy to easily obtain testing-intervals. Drawing the figures is done in the following function, againg using matplotlib.

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

Similarly, we have created a function where two parameters can be varied at the same time.
    
       
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

Drawing the figures is done with a colorbar chart, provided in matplotlib. 


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

## Task 7

By allowing sigma as parameter, all these functions could serve for task 7 as well. 

## Task 6

We created the runVraag6 function to generate figures while running the simulation with applying noise. Here we reused the fig_basius function

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


## Running the simulation

The following code starts it all up. Note that the simulation takes quite a long time. On our (pretty fast) pc it runs for nearly 8 hours. You can speed it up to run it within a reasonable timeframe to change resolutieFactor to 1 (line 407 in `game.py`), which results in lower resolution figures. 

    if(not os.path.exists("figuren")):
        os.mkdir("figuren")

    runVraag2()
    runVraag5a(0)
    runVraag5a(0.0025)
    runVraag5b(0)
    runVraag5b(0.0025)
    runVraag6()

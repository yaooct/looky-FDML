"""
Demonstrates setting up stream-in and stream-out together, then reading
stream-in values.

Connect a wire from AIN0 to DAC0 to see the effect of stream-out on
stream-in channel 0.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    NamesToAddresses:
        https://labjack.com/support/software/api/ljm/function-reference/utility/ljmnamestoaddresses
    eWriteName:
        https://labjack.com/support/software/api/ljm/function-reference/ljmewritename
    Stream Functions (eStreamRead, eStreamStart, etc.):
        https://labjack.com/support/software/api/ljm/function-reference/stream-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Stream Mode:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain
    Stream-Out:
        https://labjack.com/support/datasheets/t-series/communication/stream-mode/stream-out/stream-out-description
    Digital I/O:
        https://labjack.com/support/datasheets/t-series/digital-io
    DAC:
        https://labjack.com/support/datasheets/t-series/dac

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
"""
from datetime import datetime
import sys
import time
import numpy as np
from labjack import ljm
import ljm_stream_util

# user-defined constants
Texp = 10*1e-3 #10 ms
pulse_heights = 4.175


#Twait = 70*1e-3 #70ms
Twait = 490*1e-3 #70ms
ExTrigger_FDML = True
base_freq = 1000 # 200 frequency with which to express delays and pulse widths
pulse_onsets = int(Twait/(1/base_freq)-1) # 70 ms (2 vols at 25Hz OCT volume rate), in units of 1/base_freq, of pulse onsets
pulse_widths = int(Texp/(1/base_freq)) # 10ms; 1 widths, in units of 1/base_freq, of pulse widths 

output_channel = 'DAC0'
testing = False # provides a 5.0 in sample 0 together trigger scop
trigger_name = 'DIO0'
buffer_size = 1024
Nloops = 1

# set up buffer

n_samples = pulse_onsets + pulse_widths #np.max([a+b for a,b in zip(pulse_onsets,pulse_widths)])
n_samples = n_samples+5 # add a zero at the end to return to baseline

print(n_samples,buffer_size)

buf = np.zeros(n_samples)
buf[pulse_onsets:pulse_onsets+pulse_widths] = buf[pulse_onsets:pulse_onsets+pulse_widths]+pulse_heights
if testing:
    buf[0] = 5.0
# for po,pw,ph in zip(pulse_onsets,pulse_widths,pulse_heights):
    # buf[po:po+pw] = buf[po:po+pw]+ph
# if testing:
    # buf[0] = 5.0


# functions for trigger configuration
def configureDeviceForTriggeredStream(handle, triggerName):
    """Configure the device to wait for a trigger before beginning stream.

    @para handle: The device handle
    @type handle: int
    @para triggerName: The name of the channel that will trigger stream to start
    @type triggerName: str
    """
    address = ljm.nameToAddress(triggerName)[0]
    ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", address);

    # Clear any previous settings on triggerName's Extended Feature registers
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 0);

    # 5 enables a rising or falling edge to trigger stream
    ljm.eWriteName(handle, "%s_EF_INDEX" % triggerName, 5);#4

    # Enable
    ljm.eWriteName(handle, "%s_EF_ENABLE" % triggerName, 1);


def configureLJMForTriggeredStream():
    ljm.writeLibraryConfigS(ljm.constants.STREAM_SCANS_RETURN, ljm.constants.STREAM_SCANS_RETURN_ALL_OR_NONE)
    LJMError = ljm.writeLibraryConfigS(ljm.constants.STREAM_RECEIVE_TIMEOUT_MS, 15000)
    #print(LJMError)
    # By default, LJM will time out with an error while waiting for the stream
    # trigger to occur.

    
# initialize device    
MAX_REQUESTS = 10  # The number of eStreamRead calls that will be performed.

# Open first found LabJack
handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Setup Stream Out
OUT_NAMES = [output_channel]
NUM_OUT_CHANNELS = len(OUT_NAMES)
outAddress = ljm.nameToAddress(OUT_NAMES[0])[0]

# Allocate memory for the stream-out buffer
ljm.eWriteName(handle, "STREAM_OUT0_TARGET", outAddress)
ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_SIZE", buffer_size)
ljm.eWriteName(handle, "STREAM_OUT0_ENABLE", 1)

# Write values to the stream-out buffer
# ljm.eWriteName(handle, "STREAM_OUT0_LOOP_SIZE", n_samples)
for val in buf:
    ljm.eWriteName(handle, "STREAM_OUT0_BUFFER_F32", val)



print("STREAM_OUT0_BUFFER_STATUS = %f" % (ljm.eReadName(handle, "STREAM_OUT0_BUFFER_STATUS")))

# Stream Configuration
POS_IN_NAMES = ["AIN0", "AIN1"]
NUM_IN_CHANNELS = len(POS_IN_NAMES)

TOTAL_NUM_CHANNELS = NUM_IN_CHANNELS + NUM_OUT_CHANNELS

# Add positive channels to scan list
aScanList = ljm.namesToAddresses(NUM_IN_CHANNELS, POS_IN_NAMES)[0]
scanRate = base_freq
scansPerRead = int(scanRate/2)

# Add the scan list outputs to the end of the scan list.
# STREAM_OUT0 = 4800, STREAM_OUT1 = 4801, etc.
aScanList.extend([4800])  # STREAM_OUT0
# If we had more STREAM_OUTs
#aScanList.extend([4801])  # STREAM_OUT1
#aScanList.extend([4802])  # STREAM_OUT2
#aScanList.extend([4803])  # STREAM_OUT3

try:
    # When streaming, negative channels and ranges can be configured for
    # individual analog inputs, but the stream has only one settling time and
    # resolution.

    if deviceType == ljm.constants.dtT4:
        # LabJack T4 configuration

        # Stream settling is 0 (default) and
        # stream resolution index is 0 (default).
        aNames = ["STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
        aValues = [0, 0]
    else:
        # LabJack T7 and T8 configuration

        # Ensure triggered stream is disabled.
        ljm.eWriteName(handle, "STREAM_TRIGGER_INDEX", 0)
        # Enabling internally-clocked stream.
        ljm.eWriteName(handle, "STREAM_CLOCK_SOURCE", 0)

        # AIN0 and AIN1 ranges are +/-10 V and stream resolution index is
        # 0 (default).
        aNames = ["AIN0_RANGE", "AIN1_RANGE", "STREAM_RESOLUTION_INDEX"]
        aValues = [10.0, 10.0, 0]

        # Negative channel and settling configurations do not apply to the T8
        if deviceType == ljm.constants.dtT7:
            #     Negative Channel = 199 (Single-ended)
            #     Settling = 0 (auto)
            aNames.extend(["AIN0_NEGATIVE_CH", "STREAM_SETTLING_US",
                           "AIN1_NEGATIVE_CH"])
            aValues.extend([199, 0, 199])

    # Write the analog inputs' negative channels (when applicable), ranges,
    # stream settling time and stream resolution configuration.
    numFrames = len(aNames)
    ljm.eWriteNames(handle, numFrames, aNames, aValues)

            
    if ExTrigger_FDML:
        #apply an external trigger for stream out
        configureDeviceForTriggeredStream(handle, trigger_name)
        configureLJMForTriggeredStream()        
    
    #trigger_detected = False
    # while not trigger_detected:
        # dio_state = ljm.eReadName(handle, trigger_name)
        # if dio_state == 1:
            # trigger_detected = True
            # print("Trigger is detected.")
        # else:
            # print("No trigger") 

    # Configure and start stream
    #print(aScanList[0:TOTAL_NUM_CHANNELS])
    scanRate = ljm.eStreamStart(handle, scansPerRead, TOTAL_NUM_CHANNELS, aScanList, scanRate)
    print("\nStream started with a scan rate of %0.0f Hz." % scanRate)
    time.sleep(0.5)
    
    #########################################
    print('*********Now you can start the trigger within 10s********')
    totScans = 0
    totSkip = 0  # Total skipped samples
    i=0
    ljmScanBacklog = 0
    while i <= MAX_REQUESTS:
        ljm_stream_util.variableStreamSleep(scansPerRead, scanRate, ljmScanBacklog)   
        try:
            ret = ljm.eStreamRead(handle)
            aData = ret[0]
            ljmScanBacklog = ret[2]
            scans = len(aData) / TOTAL_NUM_CHANNELS
            totScans += scans
            # Count the skipped samples which are indicated by -9999 values. Missed
            # samples occur after a device's stream buffer overflows and are
            # reported after auto-recover mode ends.
            curSkip = aData.count(-9999.0)
            totSkip += curSkip
            print("\neStreamRead %i" % i)
            ainStr = ""
            for j in range(0, TOTAL_NUM_CHANNELS):
                ainStr += "%s = %0.5f, " % (POS_IN_NAMES[j], aData[j])
            print("  1st scan out of %i: %s" % (scans, ainStr))
            print("  Scans Skipped = %0.0f, Scan Backlogs: Device = %i, LJM = "
                  "%i" % (curSkip/TOTAL_NUM_CHANNELS, ret[1], ljmScanBacklog))
            i += 1
        except ljm.LJMError as err:
            if err.errorCode == ljm.errorcodes.NO_SCANS_RETURNED:
                sys.stdout.write('.')
                sys.stdout.flush()
                continue
            else:
                raise err       
    #########################################
    
    try:
        ljm.eStreamStop(handle)                   
    except ljm.LJMError:
        ljme = sys.exc_info()[1]
        print(ljme)
    except Exception:
        e = sys.exc_info()[1]
        print(e)
    
    
except ljm.LJMError:
    ljme = sys.exc_info()[1]
    print(ljme)
except Exception:
    e = sys.exc_info()[1]
    print(e)

# Create timestamped copy of this script as .txt file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script_copy_name = f"C:\FDML_data\{timestamp}_stimuli_{pulse_heights:.3f}V.txt"
with open(__file__, 'r') as original_script:
    with open(script_copy_name, 'w') as script_copy:
        script_copy.write(original_script.read())
print(f"Created script copy: {script_copy_name}")

# Close handle
ljm.close(handle)
print('done')
time.sleep(2) 

# ATTENTION : IDS peak est certes entièrement basé sur GenICam comme canal de communication avec nos caméras uEye+. Mais en plus de GenTL Producers pour GigE Vision® et USB3 Vision®, le kit de développement logiciel (SDK) comprend une couche de transport spéciale « uEye » grâce à laquelle les caméras uEye (matchcode « UI- ») sont également utilisables sur la base GenICam et bénéficient des nombreux avantages du nouveau SDK.

# Veuillez noter qu’en plus d’IDS peak, la dernière version d’IDS Software Suite (4.95 minimum) doit être installée. Pour plus d’information sur l’utilisation des caméras uEye dans les applications IDS peak, merci de vous référer au manuel IDS peak.
# @see : https://en.ids-imaging.com/techtipp-details/rapid-prototyping-ids-peak.html

from ids_peak import ids_peak


# Initialize library
ids_peak.Library.Initialize()

# Device manager
device_manager = ids_peak.DeviceManager.Instance()
device_manager.Update()
device_descriptors = device_manager.Devices()

# Display devices
for device_desc in device_descriptors:
    print(device_desc.DisplayName())
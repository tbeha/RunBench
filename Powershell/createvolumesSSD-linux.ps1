$hosts =,"iqn.1994-05.com.redhat:sdsdl361.vdi.local"
$hosts+=,"iqn.1994-05.com.redhat:sdsdl362.vdi.local"
$hosts+=,"iqn.1994-05.com.redhat:sdsdl363.vdi.local"
$volumes=6
$replication=2
$size=180
$login="login=192.168.58.39 username=powershell password=HPFuture15!"
$cluster="svbenchcl"
$ao=1
$thin=1

for($i=1; $i -le $volumes; $i++)
{
Invoke-Expression ('cliq createvolume volumename=Volume{0} clustername={1} size={2}GB replication={3} adaptiveoptimization={4} thinprovision={5} {6}' -f $i, $cluster, $size, $replication, $ao, $thin, $login)
Invoke-Expression ('cliq assignvolume volumename=Volume{0} initiator={1} {2}' -f $i, $hosts[$($i%3)], $login)
}
$size = 800
$ao = 0
$volumes = 18
for($i=7; $i -le $volumes; $i++)
{
Invoke-Expression ('cliq createvolume volumename=Volume{0} clustername={1} size={2}GB replication={3} adaptiveoptimization={4} thinprovision={5} {6}' -f $i, $cluster, $size, $replication, $ao, $thin, $login)
Invoke-Expression ('cliq assignvolume volumename=Volume{0} initiator={1} {2}' -f $i, $hosts[$($i%3)], $login)
}
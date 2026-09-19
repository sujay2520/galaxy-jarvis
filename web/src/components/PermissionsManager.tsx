import { Shield, Key, Check, X } from 'lucide-react';

export default function PermissionsManager() {
  const agents = ['DevBot', 'TestBot', 'DeployBot'];
  const permissionsList = ['fs.read', 'fs.write', 'shell', 'net.http', 'aws.deploy'];

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Permissions Manager</h1>
        <p className="text-gray-400 text-sm">Control what your agents are allowed to do</p>
      </div>

      <div className="bg-galaxy-800 border border-galaxy-700 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-galaxy-900 text-gray-300">
              <tr>
                <th className="px-6 py-4 font-medium flex items-center gap-2"><Shield className="w-4 h-4" /> Permission</th>
                {agents.map(a => <th key={a} className="px-6 py-4 font-medium text-center">{a}</th>)}
              </tr>
            </thead>
            <tbody className="divide-y divide-galaxy-700">
              {permissionsList.map((perm, i) => (
                <tr key={perm} className="hover:bg-galaxy-800/80 transition-colors">
                  <td className="px-6 py-4 font-mono text-galaxy-accent flex items-center gap-2">
                    <Key className="w-3 h-3 text-gray-500" /> {perm}
                  </td>
                  {agents.map((a, j) => {
                    const hasPerm = (i + j) % 2 === 0;
                    return (
                      <td key={a} className="px-6 py-4 text-center">
                        <button className={`w-8 h-8 rounded-full inline-flex items-center justify-center transition-colors ${hasPerm ? 'bg-galaxy-accent/20 text-galaxy-accent' : 'bg-galaxy-900 text-gray-600 hover:bg-galaxy-700'}`}>
                          {hasPerm ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                        </button>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

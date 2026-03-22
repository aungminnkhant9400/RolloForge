interface StatCardProps {
  label: string;
  value: number;
  color: 'green' | 'orange' | 'gray' | 'red';
}

const colorClasses = {
  green: 'bg-green-50 text-green-800 border-green-200',
  orange: 'bg-orange-50 text-orange-800 border-orange-200',
  gray: 'bg-gray-50 text-gray-800 border-gray-200',
  red: 'bg-red-50 text-red-800 border-red-200',
};

export function StatCard({ label, value, color }: StatCardProps) {
  return (
    <div className={`p-4 rounded-xl border ${colorClasses[color]}`}>
      <div className="text-sm uppercase tracking-wider opacity-70 mb-1">
        {label}
      </div>
      <div className="text-3xl font-bold">
        {value}
      </div>
    </div>
  );
}
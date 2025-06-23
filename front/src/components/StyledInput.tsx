type Props = {
  text: string;
  onClick?: () => void;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';
  placeholder?: string;
  type?: 'text' | 'password' | 'email' | 'number';
  padding?: string;
  margin?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export function StyledInput(Props: Props) {
  return (
    <input
      type={Props.type || 'text'}
      placeholder={Props.placeholder || ''}
      className={`border-2 border-[#ff782a] rounded-xl p-2 w-full ${Props.size === 'xs' ? 'text-xs' : ''} ${Props.size === 'sm' ? 'text-sm' : ''} ${Props.size === 'md' ? 'text-base' : ''} ${Props.size === 'lg' ? 'text-lg' : ''} ${Props.size === 'xl' ? 'text-xl' : ''} ${Props.size === '2xl' ? 'text-2xl' : ''} ${Props.size === '3xl' ? 'text-3xl' : ''} ${Props.padding || 'pb-2'} ${Props.margin || 'm-0'} focus:outline-none focus:ring-1 focus:ring-[#ff782a]`}
      onClick={Props.onClick}
      value={Props.value}
      onChange={Props.onChange}
    />
  );
}
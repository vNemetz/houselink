type Props = {
  text: string;
  onClick: () => void;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';
  hover?: string;
};


export function StyledButton(Props: Props) {
  return (
    <button
      className={`bg-[#ff782a] text-[#fffedf] font-bold py-2 px-4 rounded-xl hover:cursor-pointer ${Props.hover || 'hover:bg-[#d6570d]'} ${Props.size === 'xs' ? 'text-xs' : ''} ${Props.size === 'sm' ? 'text-sm' : ''} ${Props.size === 'md' ? 'text-md' : ''} ${Props.size === 'lg' ? 'text-lg' : ''} ${Props.size === 'xl' ? 'text-xl' : ''} ${Props.size === '2xl' ? 'text-2xl' : ''} ${Props.size === '3xl' ? 'text-3xl' : ''}`}
      onClick={Props.onClick}
    >
      {Props.text}
    </button>
  );
}
import { useContext } from 'react';
import { LanguageContext } from '../contexts/LanguageContext';
import React from "react";

const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useContext(LanguageContext);

  return (
    <button
      onClick={() => setLanguage(language === 'zh' ? 'en' : 'zh')}
      className="col-span-3 mx-4 py-2 rounded border text-sm"
    >
      {language === 'zh' ? 'EN' : '中文'}
    </button>
  );
};

export default LanguageSwitcher;

import React from 'react';
import { CheckCircle, AlertTriangle } from 'lucide-react';
import { Accordion, AccordionContent, AccordionHeader, AccordionItem } from './Accordion';
import ScoreBadge from './ScoreBadge';

const CategoryHeader = ({ title, categoryScore }) => {
  return (
    <div className="flex items-center gap-4">
      <p className="text-2xl font-bold text-gray-900">{title}</p>
      <ScoreBadge score={categoryScore} />
    </div>
  );
};

const CategoryContent = ({ tips }) => {
  return (
    <div className="flex flex-col gap-6 w-full">
      {/* Quick Overview Grid */}
      <div className="bg-gray-50 rounded-2xl p-6 grid md:grid-cols-2 gap-4">
        {tips.map((tip, index) => (
          <div className="flex items-center gap-3" key={index}>
            {tip.type === 'good' ? (
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
            )}
            <p className="text-gray-700 font-medium">{tip.tip}</p>
          </div>
        ))}
      </div>

      {/* Detailed Explanations */}
      <div className="flex flex-col gap-4">
        {tips.map((tip, index) => (
          <div
            key={index + tip.tip}
            className={`rounded-2xl p-6 border-2 ${
              tip.type === 'good'
                ? 'bg-green-50 border-green-200'
                : 'bg-yellow-50 border-yellow-200'
            }`}
          >
            <div className="flex items-start gap-3 mb-3">
              {tip.type === 'good' ? (
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
              )}
              <p
                className={`text-xl font-bold ${
                  tip.type === 'good' ? 'text-green-800' : 'text-yellow-800'
                }`}
              >
                {tip.tip}
              </p>
            </div>
            <p
              className={`text-base leading-relaxed ml-9 ${
                tip.type === 'good' ? 'text-green-700' : 'text-yellow-700'
              }`}
            >
              {tip.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

const Details = ({ feedback }) => {
  return (
    <div className="bg-white rounded-3xl shadow-xl w-full overflow-hidden">
      <Accordion>
        <AccordionItem id="tone-style">
          <AccordionHeader itemId="tone-style">
            <CategoryHeader title="Tone & Style" categoryScore={feedback.toneAndStyle.score} />
          </AccordionHeader>
          <AccordionContent itemId="tone-style">
            <CategoryContent tips={feedback.toneAndStyle.tips} />
          </AccordionContent>
        </AccordionItem>

        <AccordionItem id="content">
          <AccordionHeader itemId="content">
            <CategoryHeader title="Content" categoryScore={feedback.content.score} />
          </AccordionHeader>
          <AccordionContent itemId="content">
            <CategoryContent tips={feedback.content.tips} />
          </AccordionContent>
        </AccordionItem>

        <AccordionItem id="structure">
          <AccordionHeader itemId="structure">
            <CategoryHeader title="Structure" categoryScore={feedback.structure.score} />
          </AccordionHeader>
          <AccordionContent itemId="structure">
            <CategoryContent tips={feedback.structure.tips} />
          </AccordionContent>
        </AccordionItem>

        <AccordionItem id="skills">
          <AccordionHeader itemId="skills">
            <CategoryHeader title="Skills" categoryScore={feedback.skills.score} />
          </AccordionHeader>
          <AccordionContent itemId="skills">
            <CategoryContent tips={feedback.skills.tips} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

export default Details;